import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.methods.get_chat import GetChat
from aiogram import F
import aiohttp
import aiofiles
import json
import requests

import keyboards
import db_logic

API_TOKEN = '6894979902:AAEbC0-cA2Q-I29SZ5h53mGBmQwGB9ER7Ok'
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# token_kinopoisk = "2MPR2W5-BKP4DAB-KVCT0FC-6TXFK5Q"  этот токен недоступен до 21 декабря
token_kinopoisk = "Q3V3TCZ-2DT4J7P-PS0J8MK-KEHGBWG"
url = "https://api.kinopoisk.dev/v1.4/movie/random?rating.imdb=7-10&lists=top250"
headers = {
    "X-API-KEY": f"{token_kinopoisk}"
}

inline_messages = []


@dp.message(Command('start'))
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    await message.reply(f"Hello {user_id}!", reply_markup=keyboards.main_kb)

    db_logic.create_tables()


@dp.message(F.text == "Список для просмотра")
async def show_my_films(message: types.Message):
    user_id = message.from_user.id
    favorite_list = [film[1] for film in db_logic.get_liked_movies_for_user(user_id)]
    # print(favorite_list)
    favorite_str = "\n".join(favorite_list)

    await message.answer(favorite_str)



@dp.callback_query(F.data == "like")
async def save_to_my_films(callback: types.CallbackQuery):
    user_id = int(callback.from_user.id)
    await callback.message.answer("Фильм добавлен в список для просмотра")

    data = await load_json_from_file("movie_data.json")
    movie_id = data["id"]

    try:
        db_logic.insert_liked(user_id, movie_id)
    except Exception as e:
        print(f"Error: {e}")

    await callback.message.edit_reply_markup()


@dp.callback_query(F.data == "dislike")
async def save_to_bad_films(callback: types.CallbackQuery):
    user_id = int(callback.from_user.id)
    await callback.message.answer("Этот фильм больше не будет рекомендоваться")

    data = await load_json_from_file("movie_data.json")
    movie_id = data["id"]

    try:
        db_logic.insert_disliked(user_id, movie_id)
    except Exception as e:
        print(f"Error: {e}")

    await callback.message.edit_reply_markup()


@dp.message()
async def start_request(message: types.Message):
    await get_all_chats("@ruvim_shulga")

    await clean_all_inline_kb()

    user_id = message.from_user.id
    await get_movie_data(user_id)

    current_movie_data = await load_json_from_file("movie_data.json")
    poster_url = current_movie_data["poster"]["url"]

    answer_string = await get_answer_str()

    inline_message = await message.answer_photo(poster_url, answer_string, reply_markup=keyboards.react_kb)
    inline_messages.append(inline_message)


async def get_movie_data(user_id):
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers, ssl=False) as resp:
                if resp.status == 200:
                    current_movie_data = await resp.json()
                    await save_json_to_file(current_movie_data, "movie_data.json")

                    disliked_movies_id = [movie[0] for movie in db_logic.get_disliked_movies_for_user(user_id)]
                    if current_movie_data["id"] not in disliked_movies_id:
                        break

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

    try:
        db_logic.insert_movie(int(id), name, float(rating), int(year))
    except Exception as e:
        print(f"Error: {e}")

    final_list = [name, rating, year, description, *trailers_urls]

    return "\n".join(final_list)


async def clean_all_inline_kb():
    for message in inline_messages:
        try:
            await bot.edit_message_reply_markup(message.chat.id, message_id = message.message_id, reply_markup=None)
        except Exception as e:
            print(f"Error: {e}")
        inline_messages.remove(message)



async def get_user_is(username):
    user = await bot.get_chat(username)

    user_id = user.id
    print(user_id)
    return user_id


async def get_data_of_new_family_member(username):
    url = f"https://api.telegram.org/bot{API_TOKEN}/getChat?chat_id={username}"
    # print(url)
    response = requests.get(url)
    data = response.json()
    print(data)
    # user_id = data.get('result', {}).get('id')
    # chat = await bot.get_chat(chat_id=username)
    # print(chat.user.id)
    # return user_id

def send_request_in_family(username):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    params = {
        "chat_id": username,
        "text": "tolya"
    }
    response = requests.post(url, json=params)
    if response.status_code == 200:
        print("Сообщение успешно отправлено")
    else:
        print("Ошибка при отправке сообщения")


def send_message_to_user(username, message):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {"chat_id": username, "text": message}
    response = requests.post(url, json=payload)
    print(response.json())


async def get_all_chats(username):
    text = "tolye"
    await bot.send_message(username, text)


def print_db_state():
    print("Liked:\n", db_logic.print_liked())
    print()
    print("Disliked:\n", db_logic.print_disliked())
    print()
    print("ALL:\n", db_logic.print_movies())


async def main():


    print("Bot is starting...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # send_request_in_family("388610937")


    # print_db_state()
    # print(db_logic.get_liked_movies_for_user(332808756))
    asyncio.run(main())
