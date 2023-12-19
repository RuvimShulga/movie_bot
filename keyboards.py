from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Следующий фильм")]
    ],
    resize_keyboard=True
)

react_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Like", callback_data="like"),
            InlineKeyboardButton(text="Dislike", callback_data="dislike")
        ]
    ]
)
