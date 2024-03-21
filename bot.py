import asyncio
import logging
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import *
from aiogram import F
import aiohttp

import keyboards
import db_logic as db
from states import Delete, Config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot_log.txt')
        # logging.StreamHandler() 
        # строчку выше включить для отображения логов в консоль
    ]
)

with open('config.json', 'r') as f:
    config = json.load(f)
    
BOT_TOKEN = config["BOT_TOKEN"]
KINOPOISK_TOKEN = config["KINOPOISK_TOKEN"]

url = "https://api.kinopoisk.dev/v1.4/movie/random?rating.imdb=7-10&lists=top250"


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

headers = {
    "X-API-KEY": f"{KINOPOISK_TOKEN}"
}

inline_messages = []

@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    username = str(message.from_user.username)
    await db.add_user(user_id, username)

    await message.reply(f"Hello {user_id}!", reply_markup=keyboards.main_kb)

@dp.message(F.text == "Следующий фильм")
async def start_request(message: types.Message):
    global url 

    await clean_all_inline_kb()

    user_id = message.from_user.id

    while True:
        movie = await get_movie_data(url)
        await db.save_movie(movie)

        movie_id = movie["id"]

        if movie_id not in await db.get_disliked_movies_for_user(user_id):
            await prepare_and_post_movie(movie_id, message)
            break;

async def prepare_and_post_movie(movie_id, message):
    react_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Dislike", callback_data=f"dislike_{movie_id}"),
                InlineKeyboardButton(text="Like", callback_data=f"like_{movie_id}")
            ]
        ]
    )

    poster_url = await db.get_poster_url(movie_id)
    movie_info = await db.get_movie_in_one_string(movie_id)

   

    try:    
        inline_message = await message.answer_photo(poster_url, movie_info, reply_markup=react_kb, parse_mode="HTML")
    except BaseException as e:
        inline_message = await message.answer(movie_info, reply_markup=react_kb, parse_mode="HTML")
        logging.warning(f'Error when send photo with text: {e}')

    inline_messages.append(inline_message)

async def get_movie_data(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            if resp.status == 200:
                current_movie_data = await resp.json()
                # with open("data.json", 'w') as file:
                #     json.dump(current_movie_data, file, indent=4)
            
            else:
                logging.error(f"Ошибка {resp.status}: {await resp.text()}")
                
    return current_movie_data

@dp.callback_query()
async def save_to_my_films(callback: types.CallbackQuery):

    user_id = int(callback.from_user.id)

    action, movie_id = callback.data.split('_', 1)
    movie_id = int(movie_id)

    logging.info(f"{action}, {movie_id}")

    if action == 'like':
        await db.add_liked_movie(user_id, movie_id)
        await callback.message.answer("Фильм добавлен в список для просмотра")
    else:
        await db.add_disliked_movie(user_id, movie_id)
        await callback.message.answer("Этот фильм больше не будет рекомендоваться")

    await callback.message.edit_reply_markup()

@dp.message(F.text == "Нелюбимое")
async def show_disliked(message: types.Message):
    await message.answer(f"{await db.get_disliked_movies_for_user(message.from_user.id)}")

@dp.message(F.text == "Список для просмотра")
async def show_my_films(message: types.Message):
    user_id = message.from_user.id
    favorite_list = await db.get_liked_movies_for_user(user_id)

    favorite_str = "\n".join(f"{i+1}. {film}" for i,
                             film in enumerate(favorite_list))

    if favorite_str:
        await message.answer(favorite_str)
    else:
        await message.answer("В любимых ничего нет.")

@dp.message(lambda message: message.text == "Удалить из списка")
async def remove_from_favorite_list(message: types.Message, state: FSMContext):
    await state.set_state(Delete.delete_movie)
    builder = ReplyKeyboardBuilder()
    movies = await db.get_liked_movies_for_user(message.from_user.id)
    for movie in movies:
        builder.add(types.KeyboardButton(text=movie))
    builder.adjust(3)
    await message.answer(
        "Выберите фильм для удаления:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@dp.message(Delete.delete_movie)
async def delete_on_movie_name(message: types.Message, state: FSMContext):
    movie_name = message.text
    user_id = message.from_user.id

    movie_id = await db.get_movie_id(movie_name)

    await db.delete_from_liked(user_id, movie_id)

    await message.reply(f"Фильм {movie_name} успешно удален из списка", reply_markup=keyboards.main_kb)

    await state.clear()


async def get_collections_from_api():
    logging.info(await db.collections_empty())
    if await db.collections_empty():

        url = "https://api.kinopoisk.dev/v1.4/list?page=1&limit=100"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                collections = await response.json()
                collections = collections["docs"]

                for item in collections:
                    await db.save_collection(item)
                logging.info("All collections added")

@dp.message(F.text == "Параметры")
async def change_recommendation_config(message: types.Message, state: FSMContext):
    await message.answer("Выберите параметр для изменения:", reply_markup=keyboards.config_kb)

@dp.message(F.text == "Коллекции")
async def show_collections(message: types.Message, state: FSMContext):
    await state.set_state(Config.collections)
    builder = ReplyKeyboardBuilder()
    collections = await db.get_collections()
    for item in collections:
        builder.add(types.KeyboardButton(text=item.name))
    builder.adjust(2)
    await message.answer(
        "Выберите коллекцию:",
        reply_markup=builder.as_markup(resize_keyboard=True),
    )

@dp.message(Config.collections)
async def update_collections_url(message: types.Message, state: FSMContext):
    global url

    slug = await db.get_slug_on_collection_name(message.text)
    url = f"https://api.kinopoisk.dev/v1.4/movie/random?lists={slug}"
    await message.answer(f"Теперь будут рекомендоваться фильмы из коллекции {message.text}", reply_markup=keyboards.main_kb)
    await state.clear()


@dp.message()
async def search_by_name(message: types.Message):
    url = f"https://api.kinopoisk.dev/v1.4/movie/search?limit=3&query={message.text}"

    movies = await get_movie_data(url)
    movies = movies["docs"]
    
    for movie in movies:
        movie_id = movie["id"]
        
        existing_movie = await db.get_movie_by_id(movie_id)

        if existing_movie is None:
            try:
                await db.save_movie(movie)
            except BaseException as e:
                # Логирование ошибки
                logging.error(f"Error saving movie: {e}")
        await prepare_and_post_movie(movie_id, message)


async def clean_all_inline_kb():
    for message in inline_messages:
        try:
            await bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id, reply_markup=None)
        except Exception as e:
            print(f"Error: {e}")
        inline_messages.remove(message)


async def main():
    print("Bot is starting...")
    try:
        await dp.start_polling(bot)
        
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(get_collections_from_api())
    asyncio.run(main())
