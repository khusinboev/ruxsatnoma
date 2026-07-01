import logging
import re
from io import BytesIO
from typing import Optional, TypedDict

import pdfplumber

logger = logging.getLogger(__name__)


class PermitData(TypedDict):
    permit_id: str
    full_name: str
    passport_number: str
    jshshir: str
    birth_date: str
    gender: str


# "Abituriyent ruxsatnomasi" PDF fayli quyidagi qatorlarni o'z ichiga oladi:
#   ID: 6242407
#   F.I.O.: IZZATULLAYEV OTABEK SARDOR O'G'LI
#   Pasport (ID karta) seriya va raqami: AD 5769258
#   JShShIR: 50612076800047
#   Tug'ilgan sanasi: 06.12.2007
#   Jinsi: Erkak
_PATTERNS = {
    "permit_id": re.compile(r"^ID:\s*(\S+)", re.MULTILINE),
    "full_name": re.compile(r"^F\.I\.O\.:\s*(.+)$", re.MULTILINE),
    "passport_number": re.compile(r"Pasport \(ID karta\) seriya va raqami:\s*(.+)$", re.MULTILINE),
    "jshshir": re.compile(r"JShShIR:\s*(\S+)", re.MULTILINE),
    "birth_date": re.compile(r"Tug[‘’']ilgan sanasi:\s*(\S+)", re.MULTILINE),
    "gender": re.compile(r"^Jinsi:\s*(\S+)$", re.MULTILINE),
}

# Faylni "Abituriyent ruxsatnomasi" ekanligini tasdiqlash uchun sarlavha belgisi
_TITLE_MARKER = "abituriyent ruxsatnomasi"

# Bitta PDF hujjatidan qancha sahifa o'qishga urinish (haddan tashqari katta
# fayllarda vaqt yo'qotmaslik uchun)
_MAX_PAGES_TO_SCAN = 3


def _extract_text(file_bytes: bytes) -> str:
    text_parts = []
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages[:_MAX_PAGES_TO_SCAN]:
            text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts)


def parse_permit_pdf(file_bytes: bytes) -> Optional[PermitData]:
    """
    "Abituriyent ruxsatnomasi" PDF faylidan kerakli maydonlarni o'qib oladi.

    Hujjat formatga mos kelmasa yoki majburiy maydonlardan biri topilmasa,
    None qaytaradi.
    """
    try:
        text = _extract_text(file_bytes)
    except Exception:
        logger.exception("Failed to open/parse PDF file")
        return None

    if not text or _TITLE_MARKER not in text.lower():
        return None

    data: dict = {}
    for field, pattern in _PATTERNS.items():
        match = pattern.search(text)
        if not match:
            return None
        value = match.group(1).strip()
        if not value:
            return None
        data[field] = value

    return data  # type: ignore[return-value]