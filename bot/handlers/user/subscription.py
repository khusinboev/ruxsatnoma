from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.database.session import AsyncSessionLocal
from bot.services.subscription_service import SubscriptionService
from bot.keyboards.inline import get_subscription_keyboard
from bot.keyboards.user import results_reply_keyboard


router = Router()


@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    async with AsyncSessionLocal() as session:
        service = SubscriptionService(session, callback.bot)
        not_subscribed = await service.check_user_subscriptions(callback.from_user.id)

    if not not_subscribed:
        await callback.answer("Obuna tasdiqlandi ✅", show_alert=True)
        await callback.message.edit_text("Rahmat! Obuna tasdiqlandi.")
        await callback.message.answer(
            "Natijani ko'rish uchun tugmadan foydalaning:",
            reply_markup=results_reply_keyboard(),
        )
        return

    keyboard = get_subscription_keyboard(not_subscribed)
    await callback.answer("Hali ham barcha kanalga obuna bo'lmagansiz.", show_alert=True)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
