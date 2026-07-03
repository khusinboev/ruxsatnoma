from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.config.settings import settings
from bot.database.session import AsyncSessionLocal
from bot.services.subscription_service import SubscriptionService
from bot.services.permit_service import PermitService
from bot.keyboards.inline import get_subscription_keyboard, get_permit_download_keyboard
from bot.keyboards.user import main_menu_keyboard, order_section_keyboard
from bot.states.user import UserStates
from bot.handlers.user.start import WELCOME_TEXT

router = Router()


@router.message(F.text == "➕ Abituriyent ruxsatnomasi")
async def show_permit_download(message: Message):
    await message.answer(
        "Ruxsatnomani yuklab olish uchun quyidagi tugmalardan birini tanlang:",
        reply_markup=get_permit_download_keyboard(),
    )


@router.message(F.text == "🗂 Ruxsatnomaga buyurtma berish")
async def enter_order_section(message: Message, state: FSMContext):
    await state.set_state(UserStates.order_section)
    await message.answer(
        "\"Abituriyent qayd varaqasi\"ni PDF shaklida yuboring 👇",
        reply_markup=order_section_keyboard(),
    )


@router.message(F.text == "🔙 Orqaga")
async def back_to_main_menu(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())


@router.message(F.text == "📁 Buyurtmalarim")
async def show_saved_permits(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state != UserStates.order_section:
        await message.answer(
            "❗️ Bu bo'lim faqat \"🗂 Ruxsatnomaga buyurtma berish\" bo'limi ichida ishlaydi."
        )
        return

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
async def handle_text_message(message: Message, state: FSMContext):
    """Handle any plain text message from users that didn't match a known button"""
    current_state = await state.get_state()

    if current_state == UserStates.order_section:
        await message.answer(
            "📩 Iltimos, \"Abituriyent qayd varaqasi\" PDF faylini yuboring yoki "
            "\"📁 Buyurtmalarim\" tugmasidan foydalaning."
        )
        return

    await message.answer(
        "Iltimos, quyidagi bo'limlardan birini tanlang👇",
        reply_markup=main_menu_keyboard(),
    )
