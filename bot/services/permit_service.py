from dataclasses import dataclass
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config.settings import settings
from bot.database.models import Permit
from bot.database.repositories.permit_repository import PermitRepository
from bot.services.pdf_parser import parse_permit_pdf


@dataclass
class SaveResult:
    ok: bool
    message: str = ""
    permit: Optional[Permit] = None
    order_number: Optional[int] = None


class PermitService:
    """Business logic for abituriyent ruxsatnoma (permit) records"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = PermitRepository(session)

    async def save_from_pdf(
        self,
        user_id: int,
        file_bytes: bytes,
        file_id: str,
        file_unique_id: str,
    ) -> SaveResult:
        data = parse_permit_pdf(file_bytes)
        if not data:
            return SaveResult(
                ok=False,
                message=(
                    "❌ Fayldan kerakli ma'lumotlarni o'qib bo'lmadi.\n"
                    "Iltimos, \"Abituriyent ruxsatnomasi\" PDF faylini (Qayd varaqangizni) yuboring."
                ),
            )

        existing = await self.repo.get_by_user_and_permit_id(user_id, data["permit_id"])
        if existing:
            return SaveResult(
                ok=False,
                message=(
                    "ℹ️ Bu ruxsatnoma allaqachon saqlangan.\n"
                    f"Buyurtma tartib raqami: {existing.order_number}"
                ),
            )

        count = await self.repo.count_by_user(user_id)
        if count >= settings.MAX_PERMITS_PER_USER:
            return SaveResult(
                ok=False,
                message=(
                    f"⚠️ Siz maksimal {settings.MAX_PERMITS_PER_USER} ta ruxsatnoma saqlay olasiz.\n"
                    "Yangi qayd varaqasi qo'shish uchun avval eskilaridan birini o'chirtirish kerak bo'ladi."
                ),
            )

        permit = await self.repo.create(
            user_id=user_id,
            permit_id=data["permit_id"],
            full_name=data["full_name"],
            passport_number=data["passport_number"],
            jshshir=data["jshshir"],
            birth_date=data["birth_date"],
            gender=data["gender"],
            file_id=file_id,
            file_unique_id=file_unique_id,
        )

        return SaveResult(ok=True, permit=permit, order_number=permit.order_number)

    async def list_user_permits(self, user_id: int) -> List[Permit]:
        return await self.repo.get_all_by_user(user_id)