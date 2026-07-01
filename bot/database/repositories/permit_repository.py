from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from bot.database.models import Permit


class PermitRepository:
    """Repository for Permit (abituriyent ruxsatnomasi) operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_and_permit_id(self, user_id: int, permit_id: str) -> Optional[Permit]:
        result = await self.session.execute(
            select(Permit).where(
                Permit.user_id == user_id,
                Permit.permit_id == permit_id,
            )
        )
        return result.scalar_one_or_none()

    async def count_by_user(self, user_id: int) -> int:
        result = await self.session.execute(
            select(func.count(Permit.id)).where(Permit.user_id == user_id)
        )
        return result.scalar_one()

    async def get_all_by_user(self, user_id: int) -> List[Permit]:
        """Return all permits saved by a user, oldest first (save order)."""
        result = await self.session.execute(
            select(Permit)
            .where(Permit.user_id == user_id)
            .order_by(Permit.created_at.asc())
        )
        return list(result.scalars().all())

    async def create(self, **kwargs) -> Permit:
        permit = Permit(**kwargs)
        self.session.add(permit)
        await self.session.commit()
        await self.session.refresh(permit)
        return permit
