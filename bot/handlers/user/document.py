import logging
from io import BytesIO

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.exceptions import TelegramBadRequest

from bot.config.settings import settings
from bot.database.session import AsyncSessionLocal
from bot.keyboards.inline import get_subscription_keyboard
from bot.services.subscription_service import SubscriptionService
from bot.services.permit_service import PermitService
from bot.states.user import UserStates

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.document)
async def handle_permit_document(message: Message, state: FSMContext):
    """User yuborgan PDF (Qayd varaqasi) faylini qayta ishlaydi."""
    current_state = await state.get_state()
    if current_state != UserStates.order_section:
        await message.answer(
            "❗️ Fayl yuborishdan oldin \"🗂 Ruxsatnomaga buyurtma berish\" bo'limiga o'ting."
        )
        return

    document = message.document

    is_pdf = (
        document.mime_type == "application/pdf"
        or (document.file_name or "").lower().endswith(".pdf")
    )
    if not is_pdf:
        await message.answer("❗️ Iltimos, faqat PDF (.pdf) fayl yuboring.")
        return

    # Obuna faqat shu yerda (PDF yuborilganda) tekshiriladi
    async with AsyncSessionLocal() as session:
        sub_service = SubscriptionService(session, message.bot)
        not_subscribed = await sub_service.check_user_subscriptions(message.from_user.id)

    if not_subscribed:
        await message.answer(
            "❗️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz kerak:",
            reply_markup=get_subscription_keyboard(not_subscribed),
        )
        return

    max_size_bytes = settings.MAX_PDF_SIZE_MB * 1024 * 1024
    if document.file_size and document.file_size > max_size_bytes:
        await message.answer(f"❗️ Fayl hajmi {settings.MAX_PDF_SIZE_MB}MB dan oshmasligi kerak.")
        return

    processing_msg = await message.answer("⏳ Fayl tekshirilmoqda, kuting...")

    try:
        buffer = BytesIO()
        await message.bot.download(document, destination=buffer)
        file_bytes = buffer.getvalue()
    except Exception:
        logger.exception("Failed to download document from user=%s", message.from_user.id)
        await processing_msg.edit_text("❌ Faylni yuklab olishda xatolik yuz berdi. Qayta urinib ko'ring.")
        return

    async with AsyncSessionLocal() as session:
        service = PermitService(session)
        result = await service.save_from_pdf(
            user_id=message.from_user.id,
            file_bytes=file_bytes,
            file_id=document.file_id,
            file_unique_id=document.file_unique_id,
        )

    if not result.ok:
        await processing_msg.edit_text(result.message)
        return

    permit = result.permit
    me = await message.bot.get_me()

    text = (
        f"✅ <b>Tabriklaymiz!</b> : {permit.permit_id} ID raqamli abituriyent "
        f"qayd varaqasiga buyurtma qabul qilindi!\n\n"
        f"📄 Buyurtma tartib raqami: <b>{result.order_number}</b>\n\n"
        f"👤 F.I.Sh: {permit.full_name}\n\n"
        f"<i>Eslatma: Abituriyent ruxsatnomasi berilishi boshlanishi bilan ushbu bot "
        f"avtomatik ravishda ruxsatnomalaringizni sizga yuboradi!</i>\n\n"
        f"<b>Bizni kuzatishda davom eting!</b>\n\n"
        f"✔️ Buyurtma @{me.username} tomonidan amalga oshirilmoqda."
    )

    try:
        await processing_msg.edit_text(text)
    except TelegramBadRequest:
        await message.answer(text)
