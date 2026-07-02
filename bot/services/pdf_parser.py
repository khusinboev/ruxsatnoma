import logging
import re
from io import BytesIO
from typing import List, Optional, TypedDict

import pdfplumber

logger = logging.getLogger(__name__)


class PermitData(TypedDict):
    permit_id: str
    full_name: str
    passport_number: str
    jshshir: str
    birth_date: str
    gender: str


# "Abituriyent qayd varaqasi" PDF fayli ikki ustunli jadval ko'rinishida:
# chap ustunda maydon nomi (label), o'ng ustunda uning qiymati turadi, masalan:
#   ID: 6089171
#   F.I.O.: MAXMUDJONOVA MUSHTARIYBONU BOXODIR QIZI
#   Pasport (ID karta) seriya va raqami: AD 9108786
#   JShShIR: 62106096750031
#   Tug'ilgan sanasi: 21.06.2009
#   Jinsi: Ayol
#
# F.I.O. kabi uzun qiymatlar PDF'da bir necha qatorga bo'linadi, va sahifa
# matnini yuqoridan-pastga o'qiganda label shu qatorlar orasiga tushib qoladi
# (masalan "ISM FAMILIYA\nF.I.O.:\nSHARIF" tartibida). Shu sababli maydonlar
# oddiy qator-bo'yicha regex bilan emas, so'zlarning sahifadagi
# koordinatalari orqali o'qiladi: labellar sahifaning chap yarmida, ularga
# mos qiymatlar o'ng yarmida joylashgan bo'ladi.
_FIELDS = [
    ("permit_id", re.compile(r"^ID:")),
    ("full_name", re.compile(r"^F\.I\.O\.:")),
    ("passport_number", re.compile(r"^Pasport \(ID karta\) seriya va raqami:")),
    ("jshshir", re.compile(r"^JShShIR:")),
    ("birth_date", re.compile(r"^Tug[‘’']ilgan sanasi:")),
    ("gender", re.compile(r"^Jinsi:")),
]

# Kerakli maydonlardan keyin keladigan birinchi label — Jinsi qatorining
# qiymat zonasini pastdan chegaralash uchun ishlatiladi, o'zi o'qilmaydi.
# Ba'zi PDF'larda bu qatorning qiymati ham chap yarmiga "sizib" kirishi
# mumkin (masalan uzun manzil), shu sababli oxiriga $ qo'yilmagan.
_BOUNDARY_LABEL = re.compile(r"^Doimiy yashash manzili:")

# Faylni "Abituriyent qayd varaqasi" ekanligini tasdiqlash uchun sarlavha belgisi
_TITLE_MARKER = "abituriyent qayd varaqasi"

# Bitta PDF hujjatidan qancha sahifa o'qishga urinish (haddan tashqari katta
# fayllarda vaqt yo'qotmaslik uchun)
_MAX_PAGES_TO_SCAN = 3

# Bir xil "qator" deb hisoblanadigan so'zlar orasidagi balandlik farqi (pt)
_LINE_TOLERANCE = 3


def _group_into_lines(words: List[dict]) -> List[dict]:
    """So'zlarni bir xil balandlikdagi (top) qatorlarga guruhlaydi."""
    lines: List[dict] = []
    for word in sorted(words, key=lambda w: w["top"]):
        if lines and word["top"] - lines[-1]["top"] <= _LINE_TOLERANCE:
            lines[-1]["words"].append(word)
        else:
            lines.append({"top": word["top"], "words": [word]})
    return lines


def _line_text(line: dict) -> str:
    return " ".join(w["text"] for w in sorted(line["words"], key=lambda w: w["x0"]))


def _extract_fields_from_page(page) -> Optional[dict]:
    words = page.extract_words()
    if not words:
        return None

    mid_x = page.width / 2
    label_words = [w for w in words if w["x0"] < mid_x]
    value_words = [w for w in words if w["x0"] >= mid_x]

    matches = []  # (top, field)
    boundary_top: Optional[float] = None
    for line in _group_into_lines(label_words):
        text = _line_text(line)
        for field, pattern in _FIELDS:
            if pattern.match(text):
                matches.append((line["top"], field))
                break
        else:
            if boundary_top is None and _BOUNDARY_LABEL.match(text):
                boundary_top = line["top"]

    if len(matches) != len(_FIELDS) or boundary_top is None:
        return None

    matches.sort(key=lambda m: m[0])
    tops = [top for top, _ in matches] + [boundary_top]

    data = {}
    for i, (top, field) in enumerate(matches):
        if i == 0:
            # Birinchi maydondan oldin "avvalgi maydon" yo'q — navbatdagi
            # ikkita maydon orasidagi bo'shliqni orqaga qarab ko'chirib,
            # sahifa sarlavhasidagi bog'liq bo'lmagan matnni chetlab o'tamiz.
            lower = top - (tops[1] - top) / 2
        else:
            lower = (tops[i - 1] + top) / 2
        upper = (top + tops[i + 1]) / 2

        band_words = [w for w in value_words if lower <= w["top"] < upper]
        band_words.sort(key=lambda w: (w["top"], w["x0"]))
        value = " ".join(w["text"] for w in band_words).strip()
        if not value:
            return None
        data[field] = value

    return data


def parse_permit_pdf(file_bytes: bytes) -> Optional[PermitData]:
    """
    "Abituriyent qayd varaqasi" PDF faylidan kerakli maydonlarni o'qib oladi.

    Hujjat formatga mos kelmasa yoki majburiy maydonlardan biri topilmasa,
    None qaytaradi.
    """
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            pages = pdf.pages[:_MAX_PAGES_TO_SCAN]
            text = "\n".join(page.extract_text() or "" for page in pages)
            if not text or _TITLE_MARKER not in text.lower():
                return None

            for page in pages:
                data = _extract_fields_from_page(page)
                if data:
                    return data  # type: ignore[return-value]
    except Exception:
        logger.exception("Failed to open/parse PDF file")
        return None

    return None
