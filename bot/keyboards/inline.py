from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List
from bot.database.models import Channel, PermitAppButton


def get_subscription_keyboard(channels: List[Channel]) -> InlineKeyboardMarkup:
    """Create keyboard with subscription channels"""
    buttons = []
    
    for channel in channels:
        buttons.append([
            InlineKeyboardButton(
                text=channel.button_text,
                url=channel.button_url,
            )
        ])
    
    # Add check button
    buttons.append([
        InlineKeyboardButton(
            text="✅ Obunani tekshirish",
            callback_data="check_subscription"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_permit_download_keyboard(buttons: List[PermitAppButton]) -> InlineKeyboardMarkup:
    """Ruxsatnomani yuklab olish uchun admin tomonidan qo'shilgan havolali tugmalar"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=button.button_text, url=button.button_url)]
        for button in buttons
    ])
