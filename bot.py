import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram import F
import aiohttp
import json

import keyboards
import db_logic as db
from states import Form, Family, Choice, Mode, CurrentMovie, Delete


with open('config.json', 'r') as f:
    config = json.load(f)
    
BOT_TOKEN = config["BOT_TOKEN"]
KINOPOISK_TOKEN = config["KINOPOISK_TOKEN"]

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


url = "https://api.kinopoisk.dev/v1.4/movie/random?rating.imdb=7-10&lists=top250"
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
async def start_request(message: types.Message, state: FSMContext):

    await clean_all_inline_kb()

    user_id = message.from_user.id

    movie = await get_movie_data(user_id)
    movie_id = movie["id"]
        
    await state.update_data(movie_id=movie_id)

    poster_url = await db.get_poster_url(movie_id)
    movie_info = await db.get_movie_in_one_string(movie_id)

    inline_message = await message.answer_photo(poster_url, movie_info, reply_markup=keyboards.react_kb, parse_mode="HTML")
    inline_messages.append(inline_message)


async def get_movie_data(user_id):
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(url, headers=headers, ssl=False) as resp:
                if resp.status == 200:
                    current_movie_data = await resp.json()
                    await db.save_movie(current_movie_data)

                    if current_movie_data["id"] not in await db.get_disliked_movies_for_user(user_id):
                        break
                else:
                    print(f"Ошибка {resp.status}: {await resp.text()}")
                    break 

    return current_movie_data



@dp.callback_query(F.data == "like")
async def save_to_my_films(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Фильм добавлен в список для просмотра")
    
    data =  await state.get_data()
    user_id = int(callback.from_user.id)
    movie_id = data.get("movie_id")

    await db.add_liked_movie(user_id, movie_id)

    await callback.message.edit_reply_markup()


@dp.callback_query(F.data == "dislike")
async def save_to_bad_films(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Этот фильм больше не будет рекомендоваться")

    data =  await state.get_data()
    user_id = int(callback.from_user.id)
    movie_id = data.get("movie_id")

    await db.add_disliked_movie(user_id, movie_id)

    await callback.message.edit_reply_markup()

@dp.message(F.text == "Нелюбимое")
async def show_disliked(message: types.Message, state: FSMContext):
    await message.answer(f"{await db.get_disliked_movies_for_user(message.from_user.id)}")


@dp.message(F.text == "Список для просмотра")
async def show_my_films(message: types.Message):
    user_id = message.from_user.id
    favorite_list = await db.get_liked_movies_for_user(user_id)

    favorite_str = "\n".join(f"{i+1}. {film}" for i,
                             film in enumerate(favorite_list))

    await message.answer(favorite_str)


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
        reply_markup=builder.as_markup(resize_keyboard=True, one_time_keyboard=True),
    )

@dp.message(Delete.delete_movie)
async def delete_on_movie_name(message: types.Message, state: FSMContext):
    movie_name = message.text
    user_id = message.from_user.id

    movie_id = await db.get_movie_id(movie_name)

    await db.delete_from_liked(user_id, movie_id)

    await message.reply(f"Фильм {movie_name} успешно удален из списка", reply_markup=keyboards.main_kb)

# async def get_recommendation(user_id):
#     recommendation = orm.session.query(orm.UserRecommendation).filter(
#         orm.UserRecommendation.user_id == user_id).first()

#     if recommendation:
#         rec_movie = recommendation.recommended_movie_id
#         orm.session.delete(recommendation)
#         orm.session.commit()

#         return rec_movie
#     return None


# @dp.message(F.text == "Одиночный режим")
# async def single_mode(message: types.Message):
#     await message.answer("Теперь вы можете выбирать фильмы в свою собственную коллекцию!", reply_markup=keyboards.main_kb)


# @dp.message(F.text == "Создать семью")
# async def create_family(message: types.Message, state: FSMContext):
#     await state.set_state(Family.family_name)
#     await message.answer("Введите название для вашей семьи")


# @dp.message(Family.family_name)
# async def create_family_with_name(message: types.Message, state: FSMContext):
#     family_name = message.text
#     family = orm.Family(family_name=family_name, owner=message.from_user.id)
#     orm.session.add(family)
#     orm.session.commit()
#     await add_owner_in_family(message.from_user.id)

#     await message.answer(f"Семья {family_name} успешно создана")
#     await state.clear()


# @dp.message(F.text == "Выбрать семью")
# async def select_family(message: types.Message, state: FSMContext):
#     families = orm.session.query(orm.Family).all()
#     for family in families:
#         family_button = keyboards.KeyboardButton(text=family.family_name)
#         keyboards.select_family_kb.keyboard[0].append(family_button)

#     await state.set_state(Choice.choice)
#     await message.answer("С помощью кнопок выберите семью", reply_markup=keyboards.select_family_kb)


# @dp.message(Choice.choice)
# async def move_to_family_room(message: types.Message, state: FSMContext):
#     family = message.text

#     await state.set_state(Mode.mode)
#     await state.update_data(mode=family)
#     print(await state.get_data())
#     # await state.update_data(choice=family)
#     await message.answer(f"Вы успешно переключились на комнату семьи {family}", reply_markup=keyboards.main_kb)





# @dp.message(F.text == "Текущая семья")
# async def current_family(message: types.Message, state: FSMContext):
#     data = await state.get_data()
#     current_family_name = data.get("mode")
#     current_family_id = orm.session.query(orm.Family.id).filter(
#         orm.Family.family_name == current_family_name).first()[0]
#     # print(orm.session.query(orm.UsersInFamily).all())
#     member_of_family = orm.session.query(orm.UsersInFamily.user_id).filter(
#         orm.UsersInFamily.family_id == current_family_id).all()
#     print(member_of_family)

#     print(current_family_name, current_family_id)





# @dp.callback_query(F.data == "accept")
# async def accepting_in_family(callback: types.CallbackQuery, state: FSMContext):
#     order = orm.session.query(orm.Order).filter(
#         orm.Order.to_user == callback.from_user.id).all()[-1]
#     order.status = "accepted"

#     await add_user_in_family(callback.from_user.id, order.family)

#     await callback.message.answer("Теперь вы в семье!")
#     await bot.send_message(order.from_user, f"Ваш запрос к {db.get_username(order.to_user)} был принят!")

#     orm.session.commit()

#     await callback.message.edit_reply_markup()


# @dp.callback_query(F.data == "reject")
# async def rejecting(callback: types.CallbackQuery):
#     order = orm.session.query(orm.Order).filter(
#         orm.Order.to_user == callback.from_user.id).first()
#     order.status = "rejected"

#     await callback.message.answer("Запрос отклонен")
#     await bot.send_message(order.from_user, f"Ваш запрос к {db.get_username(order.to_user)} был отклонен")

#     orm.session.commit()

#     await callback.message.edit_reply_markup()


# @dp.message(F.text == "Добавить в семью")
# async def add_user_to_family(message: types.Message, state: FSMContext):
#     await state.set_state(Form.username)
#     await message.answer("Введите username пользователя, которого хотите добавить в семью. @ не нужна!")


# @dp.message(Form.username)
# async def form_username(message: types.Message, state: FSMContext):
#     await state.update_data(username=message.text)
#     data = await state.get_data()

#     to_family = data.get("mode")
#     to_family_id = orm.session.query(orm.Family.id).filter(
#         orm.Family.family_name == to_family).first()[0]

#     print(to_family_id)
#     from_username = message.from_user.username
#     from_user_id = message.from_user.id

#     to_username = data.get("username")
#     try:
#         to_user_id = db.get_user_id(to_username)
#         await validation_and_send_request(to_family_id, from_username, to_username, from_user_id, to_user_id)
#     except BaseException as e:
#         await message.answer(f"Пользователь {to_username} не подключен к боту.")
#         print(e)





# async def add_recommendation(user_id, movie_id):
#     families = orm.session.query(orm.UsersInFamily.family_id).filter(
#         orm.UsersInFamily.user_id == user_id).all()
#     # print(families)

#     for family in families:
#         users_in_family = orm.session.query(orm.UsersInFamily.user_id).filter(
#             orm.UsersInFamily.family_id == family[0]).all()
#         # print(users_in_family)
#         for user in users_in_family:
#             if user[0] == user_id:
#                 continue
#             new_rec = orm.UserRecommendation(
#                 user_id=user[0], recommended_movie_id=movie_id)
#             orm.session.add(new_rec)
#             orm.session.commit()





# async def add_user_in_family(user_id, family_id):
#     user_family = orm.UsersInFamily(user_id=user_id, family_id=family_id)
#     orm.session.add(user_family)
#     orm.session.commit()


# async def add_owner_in_family(user_id):
#     family_id = orm.session.query(orm.Family.id).filter(
#         orm.Family.owner == user_id).all()[-1][0]
#     await add_user_in_family(user_id, family_id)


# async def validation_and_send_request(to_family_id, from_username, to_username, from_user_id, to_user_id):
    # resend = False
    # order_exists = False
    # try:
    #     all_request_from_user = orm.session.query(orm.Order).filter(
    #         orm.Order.from_user == from_user_id).all()
    # except BaseException:
    #     print("its first order")

    # for request in all_request_from_user:
    #     if request.to_user == to_user_id and request.family == to_family_id:
    #         order_exists = True
    #         await bot.send_message(from_user_id, f"Вы уже отправили запрос этому пользователю. Статус: {request.status}")
    #         if request.status == 'rejected':
    #             resend = True
    #             await bot.send_message(from_user_id, "Запрос будет отправлен снова, так как был отклонен")
    #         break
    # else:
    #     order = orm.Order(from_user=from_user_id, to_user=to_user_id,
    #                       family=to_family_id, status='awaiting')
    #     orm.session.add(order)
    #     orm.session.commit()

    # if resend or not order_exists:
    #     await send_request_in_family(from_username, to_user_id)
    #     await bot.send_message(from_user_id, f"Запрос успешно отправлен пользователю {to_username}")


async def clean_all_inline_kb():
    for message in inline_messages:
        try:
            await bot.edit_message_reply_markup(message.chat.id, message_id=message.message_id, reply_markup=None)
        except Exception as e:
            print(f"Error: {e}")
        inline_messages.remove(message)


# async def send_request_in_family(from_username, to_user_id):
#     message = f"Вам пришел запрос на добавление в семью от {from_username}"
#     await bot.send_message(to_user_id, message, reply_markup=keyboards.family_kb)


async def main():
    print("Bot is starting...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
