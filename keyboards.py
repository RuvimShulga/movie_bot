from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Следующий фильм")],
        [KeyboardButton(text="Список для просмотра"),
         KeyboardButton(text="Удалить из списка")],
         [KeyboardButton(text="Добавить в семью")]
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

family_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Отклонить", callback_data="reject"),
            InlineKeyboardButton(text="Принять", callback_data="accept")
        ]
    ]
)
