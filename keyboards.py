from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Следующий фильм"),
         KeyboardButton(text="Параметры")],
        [KeyboardButton(text="Список для просмотра"),
         KeyboardButton(text="Удалить из списка")],
    ],
    resize_keyboard=True
)

config_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Коллекции")],
    ],
    resize_keyboard=True
)

react_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Dislike", callback_data="dislike"),
            InlineKeyboardButton(text="Like", callback_data="like")
        ]
    ]
)
