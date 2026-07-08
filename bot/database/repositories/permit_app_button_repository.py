from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from bot.database.models import PermitAppButton


class PermitAppButtonRepository:
    """Repository for PermitAppButton (webapp/havola tugmalari) operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> List[PermitAppButton]:
        """Get all buttons ordered by priority, then insertion order"""
        result = await self.session.execute(
            select(PermitAppButton).order_by(
                PermitAppButton.priority.desc(), PermitAppButton.id.asc()
            )
        )
        return list(result.scalars().all())

    async def get_by_text_and_url(self, button_text: str, button_url: str) -> Optional[PermitAppButton]:
        result = await self.session.execute(
            select(PermitAppButton).where(
                PermitAppButton.button_text == button_text,
                PermitAppButton.button_url == button_url,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, **kwargs) -> PermitAppButton:
        button = PermitAppButton(**kwargs)
        self.session.add(button)
        await self.session.commit()
        await self.session.refresh(button)
        return button

    async def delete(self, button: PermitAppButton) -> None:
        await self.session.delete(button)
        await self.session.commit()
