from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.services.user_service import UserService
from bot.database.session import AsyncSessionLocal
from bot.keyboards.user import main_menu_keyboard

router = Router()

WELCOME_TEXT = (
    "Abituriyent ruxsatnomasini yuklab beruvchi va unga buyurtma qabul qiluvchi botga xush kelibsiz!\n\n"
    "<b>Quyidagi bo'limlardan birini tanlang👇</b>"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command. Obuna bu yerda so'ralmaydi."""
    await state.clear()

    async with AsyncSessionLocal() as session:
        user_service = UserService(session)
        await user_service.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code,
        )

    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())
