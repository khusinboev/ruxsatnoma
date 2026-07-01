from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup, KeyboardButton

from bot.config.settings import settings
from bot.database.session import AsyncSessionLocal
from bot.services.user_service import UserService


def phone_request_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Telefon raqam yuborish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


class RegistrationMiddleware(BaseMiddleware):
    """Force phone registration for every non-admin user."""

    async def __call__(
        self,
        handler: Callable[[Any, Dict[str, Any]], Awaitable[Any]],
        event: Any,
        data: Dict[str, Any],
    ) -> Any:
        from_user = getattr(event, "from_user", None)
        if not from_user:
            return await handler(event, data)

        if from_user.id in settings.ADMIN_USER_IDS:
            return await handler(event, data)

        async with AsyncSessionLocal() as session:
            user_service = UserService(session)
            user = await user_service.get_or_create_user(
                telegram_id=from_user.id,
                username=from_user.username,
                first_name=from_user.first_name,
                last_name=from_user.last_name,
                language_code=from_user.language_code,
            )

        has_phone = bool((user.phone_number or "").strip())
        if has_phone:
            return await handler(event, data)

        if isinstance(event, Message):
            # Let valid contact messages pass to the dedicated contact handler.
            if event.contact and (not event.contact.user_id or event.contact.user_id == from_user.id):
                return await handler(event, data)

            await event.answer(
                "❗️Botdan foydalanish uchun telefon raqamingizni yuborish majburiy.",
                reply_markup=phone_request_keyboard(),
            )
            return

        if isinstance(event, CallbackQuery):
            await event.answer(
                "Avval telefon raqamingizni yuboring.",
                show_alert=True,
            )
            if event.message:
                await event.message.answer(
                    "Telefon raqamingizni yubormaguningizcha botdan foydalana olmaysiz.",
                    reply_markup=phone_request_keyboard(),
                )
            return

        return await handler(event, data)
