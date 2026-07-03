from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Abituriyent ruxsatnomasi")],
            [KeyboardButton(text="🗂 Ruxsatnomaga buyurtma berish")],
            [KeyboardButton(text="📁 Buyurtmalarim")],

        ],
        resize_keyboard=True,
    )


def order_section_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔙 Orqaga")],
        ],
        resize_keyboard=True,
    )
