from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Одиночный режим")],
        [KeyboardButton(text="Создать семью")],
        [KeyboardButton(text="Выбрать семью")]
    ],
    resize_keyboard=True

)


main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Следующий фильм")],
        [KeyboardButton(text="Список для просмотра"),
         KeyboardButton(text="Удалить из списка")],
        # [KeyboardButton(text="Выбрать семью"),
        #  KeyboardButton(text="Добавить в семью")],
        # [KeyboardButton(text="Текущая семья")]
    ],
    resize_keyboard=True
)

select_family_kb = ReplyKeyboardMarkup(
    keyboard=[[]],
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
