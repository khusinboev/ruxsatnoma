from aiogram import Router, F
from aiogram.types import Message

from bot.config.settings import settings
from bot.database.session import AsyncSessionLocal
from bot.services.subscription_service import SubscriptionService
from bot.services.permit_service import PermitService
from bot.keyboards.inline import get_subscription_keyboard

router = Router()


@router.message(F.text == "📊 Saqlanganlarni ko'rish")
async def show_results_links(message: Message):
    # Obuna faqat shu tugma bosilganda tekshiriladi
    async with AsyncSessionLocal() as session:
        sub_service = SubscriptionService(session, message.bot)
        not_subscribed = await sub_service.check_user_subscriptions(message.from_user.id)

    if not_subscribed:
        await message.answer(
            "❗️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz kerak:",
            reply_markup=get_subscription_keyboard(not_subscribed),
        )
        return

    async with AsyncSessionLocal() as session:
        service = PermitService(session)
        permits = await service.list_user_permits(message.from_user.id)

    if not permits:
        await message.answer(
            "Sizda hali saqlangan qayd varaqa yo'q.\n"
            "\"Abituriyent qayd varaqasi\" PDF faylini yuboring."
        )
        return

    lines = ["📋 <b>Saqlangan qayd varaqalaringiz:</b>\n"]
    for idx, permit in enumerate(permits, start=1):
        lines.append(f"{idx}. {permit.permit_id} - {permit.full_name}")
    lines.append(f"\nJami: {len(permits)}/{settings.MAX_PERMITS_PER_USER}")

    await message.answer("\n".join(lines))


@router.message(F.text)
async def handle_text_message(message: Message):
    """Handle any plain text message from users"""
    await message.answer(
        "📩 Iltimos, \"Abituriyent qayd varaqasi\" PDF faylini yuboring yoki "
        "\"📊 Saqlanganlarni ko'rish\" tugmasidan foydalaning."
    )
