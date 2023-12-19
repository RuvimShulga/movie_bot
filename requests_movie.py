import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
import aiohttp
import aiofiles
import json

import keyboards
import db_logic

API_TOKEN = '6894979902:AAEbC0-cA2Q-I29SZ5h53mGBmQwGB9ER7Ok'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

token_kinopoisk = "2MPR2W5-BKP4DAB-KVCT0FC-6TXFK5Q"
url = "https://api.kinopoisk.dev/v1.4/movie/random?rating.imdb=7-10&lists=top250"
headers = {
    "X-API-KEY": f"{token_kinopoisk}"
}


@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    await message.reply(f"Hello {user_id}!", reply_markup=keyboards.main_kb)

    db_logic.create_tables()


@dp.message(F.text == "Список для просмотра")
async def show_my_films(message: types.Message):
    user_id = message.from_user.id
    favorite_list = [film[0] for film in db_logic.get_liked_movies_for_user(user_id)]
    favorite_str = "\n".join(favorite_list)

    await message.answer(favorite_str)



@dp.callback_query(F.data == "like")
async def save_to_my_films(callback: types.CallbackQuery):
    user_id = int(callback.from_user.id)
    await callback.message.answer("хороший выбор")

    data = await load_json_from_file("movie_data.json")
    movie_id = data["id"]

    try:
        db_logic.insert_liked(user_id, movie_id)
    except Exception as e:
        print(f"Error: {e}")


@dp.callback_query(F.data == "dislike")
async def save_to_bad_films(callback: types.CallbackQuery):
    user_id = int(callback.from_user.id)
    await callback.message.answer("понял твой выбор")

    data = await load_json_from_file("movie_data.json")
    movie_id = data["id"]

    try:
        db_logic.insert_disliked(user_id, movie_id)
    except Exception as e:
        print(f"Error: {e}")


@dp.message()
async def start_request(message: types.Message):
    await get_movie_data()

    current_movie_data = await load_json_from_file("movie_data.json")
    poster_url = current_movie_data["poster"]["url"]

    answer_string = await get_answer_str()

    await message.answer_photo(poster_url, answer_string, reply_markup=keyboards.react_kb)


async def get_movie_data():
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            if resp.status == 200:
                current_movie_data = await resp.json()
                await save_json_to_file(current_movie_data, "movie_data.json")

            else:
                print(f"Ошибка {resp.status}: {await resp.text()}")


async def save_json_to_file(json_data, filename):
    async with aiofiles.open(filename, "w") as file:
        await file.write(json.dumps(json_data))


async def load_json_from_file(filename):
    async with aiofiles.open(filename, "r") as file:
        file_content = await file.read()
        return json.loads(file_content)


async def get_answer_str():
    current_movie_data = await load_json_from_file("movie_data.json")

    id = str(current_movie_data["id"])
    name = str(current_movie_data["names"][0]["name"])
    rating = str(current_movie_data["rating"]["imdb"])
    year = str(current_movie_data["year"])
    description = str(current_movie_data["description"])
    trailers_urls = [trailer["url"] for trailer in current_movie_data["videos"]["trailers"]]

    db_logic.insert_movie(int(id), name, float(rating), int(year))

    final_list = [name, rating, year, description, *trailers_urls]

    return "\n".join(final_list)


def print_db_state():
    print("Liked:\n", db_logic.print_liked())
    print()
    print("Disliked:\n", db_logic.print_disliked())
    print()
    print("ALL:\n", db_logic.print_movies())


async def main():
    print("Bot is starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    # print_db_state()
    print(db_logic.get_liked_movies_for_user(332808756))
    asyncio.run(main())
