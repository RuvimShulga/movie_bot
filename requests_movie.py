import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram import F
import aiohttp
import aiofiles
import json
import requests

import keyboards
from db_logic import Database
from states import Form
import orders

db = Database('movies.db')

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
    username = str(message.from_user.username)
    if not db.user_exists(user_id):
        db.add_user(user_id, username)

    await message.reply(f"Hello {user_id}!", reply_markup=keyboards.main_kb)



@dp.message(F.text == "Список для просмотра")
async def show_my_films(message: types.Message):
    user_id = message.from_user.id
    favorite_list = [film[1] for film in    db.get_liked_movies_for_user(user_id)]
    
    favorite_str = "\n".join(f"{i+1}. {film}" for i, film in enumerate(favorite_list))

    await message.answer(favorite_str)


@dp.message(F.text == "Удалить из списка")
async def remove_from_favorite_list(message: types.Message):
    await show_my_films(message)

    await message.answer("Введите целое число - номер просмотренного фильма")

    try:
        # Ждем ответ от пользователя, таймаут можно установить по вашему усмотрению
        response = await bot.wait_for('message', timeout=100)
        movie_number_in_list = int(response.text)
    except Exception as e:
        print(f"Error: {e}")

    print(movie_number_in_list)
    #   db.delete_liked(user_id, liked_movie_id)



@dp.callback_query(F.data == "like")
async def save_to_my_films(callback: types.CallbackQuery):
    user_id = int(callback.from_user.id)
    await callback.message.answer("Фильм добавлен в список для просмотра")

    data = await load_json_from_file("movie_data.json")
    movie_id = data["id"]

    try:
        db.insert_liked(user_id, movie_id)
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
        db.insert_disliked(user_id, movie_id)
    except Exception as e:
        print(f"Error: {e}")

    await callback.message.edit_reply_markup()


@dp.callback_query(F.data == "accept")
async def accepting_in_family(callback: types.CallbackQuery):
    order = orders.session.query(orders.Order).filter(orders.Order.to_user == callback.from_user.id).first()
    order.status = "accepted"

    await callback.message.answer("Теперь вы в семье!")
    await bot.send_message(order.from_user, f"Ваш запрос к {db.get_username(order.to_user)} был принят!")

    orders.session.commit()

    await callback.message.edit_reply_markup()


@dp.callback_query(F.data == "reject")
async def rejecting(callback: types.CallbackQuery):
    order = orders.session.query(orders.Order).filter(orders.Order.to_user == callback.from_user.id).first()
    order.status = "rejected"

    await callback.message.answer("Запрос отклонен")
    await bot.send_message(order.from_user, f"Ваш запрос к {db.get_username(order.to_user)} был отклонен")

    orders.session.commit()

    await callback.message.edit_reply_markup()


@dp.message(F.text == "Добавить в семью")
async def add_user_to_family(message: types.Message, state: FSMContext):
    await state.set_state(Form.username)
    await message.answer("Введите username пользователя, которого хотите добавить в семью. @ не нужна!")
    

@dp.message(Form.username)
async def form_username(message: types.Message, state: FSMContext):
    await state.update_data(username=message.text)
    data = await state.get_data()
    await state.clear()

    from_username = message.from_user.username
    from_user_id = message.from_user.id

    to_username = data.get("username")
    try:
        to_user_id = db.get_user_id(to_username)
        await validation_and_send_request(from_username, to_username, from_user_id, to_user_id)
    except BaseException as e:
        await message.answer(f"Пользователь {to_username} не подключен к боту.")
        print(f"error: {e}")


@dp.message()
async def start_request(message: types.Message):

    await clean_all_inline_kb()

    user_id = message.from_user.id
    await get_movie_data(user_id)

    current_movie_data = await load_json_from_file("movie_data.json")
    poster_url = current_movie_data["poster"]["url"]

    answer_string = await get_answer_str()

    inline_message = await message.answer_photo(poster_url, answer_string, reply_markup=keyboards.react_kb)
    inline_messages.append(inline_message)


async def validation_and_send_request(from_username, to_username, from_user_id, to_user_id):
    resend = False
    order_exists = False
    all_request_from_user = orders.session.query(orders.Order).filter(orders.Order.from_user == from_user_id).all()
    for request in all_request_from_user:
        if request.to_user == to_user_id:
            order_exists = True
            await bot.send_message(from_user_id, f"Вы уже отправили запрос этому пользователю. Статус: {request.status}")
            if request.status == 'rejected':
                resend = True
                await bot.send_message(from_user_id, "Запрос будет отправлен снова, так как был отклонен")
            break
    else:
        order = orders.Order(from_user=from_user_id, to_user=to_user_id, status='awaiting')
        orders.session.add(order)
        orders.session.commit()

    if resend or not order_exists:
        await send_request_in_family(from_username, to_user_id)
        await bot.send_message(from_user_id, f"Запрос успешно отправлен пользователю {to_username}")


async def get_movie_data(user_id):
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers, ssl=False) as resp:
                if resp.status == 200:
                    current_movie_data = await resp.json()
                    await save_json_to_file(current_movie_data, "movie_data.json")

                    disliked_movies_id = [movie[0] for movie in db.get_disliked_movies_for_user(user_id)]
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
        db.insert_movie(int(id), name, float(rating), int(year))
    except Exception as e:
        print(f"Error: {e}")

    final_list = [name, rating, year, description, *trailers_urls]

    return "\n".join(final_list)


async def clean_all_inline_kb():
    for message in inline_messages:
        try:
            await bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id, reply_markup=None)
        except Exception as e:
            print(f"Error: {e}")
        inline_messages.remove(message)


async def send_request_in_family(from_username, to_user_id):
    message = f"Вам пришел запрос на добавление в семью от {from_username}"
    await bot.send_message(to_user_id, message, reply_markup=keyboards.family_kb)



def print_db_state():
    print("Liked:\n",   db.print_liked())
    print()
    print("Disliked:\n",    db.print_disliked())
    print()
    print("ALL:\n", db.print_movies())


async def main():
    db.delete_orders()
    print("Bot is starting...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
