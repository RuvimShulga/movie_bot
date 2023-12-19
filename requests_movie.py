import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
import aiohttp

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
    await message.reply("Hello!")


@dp.message()
async def start_request(message: types.Message):
    response_list = await get_movie()

    poster_url = response_list[0]

    response_list.pop(0)
    response_str = "\n".join(map(str, response_list))

    await message.answer_photo(poster_url, response_str)


async def get_movie():
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, ssl=False) as resp:
            if resp.status == 200:
                data = await resp.json()

                img = data["poster"]["url"]
                name = data["names"][0]["name"]
                rating = data["rating"]["imdb"]
                year = data["year"]
                description = data["description"]

                trailers_urls = [trailer["url"] for trailer in data["videos"]["trailers"]]

                print(name)
                print(rating)
                print(year)
                print(description)
                print(*trailers_urls, sep="\n")

                return [img, name, rating, year, description, *trailers_urls]

            else:
                print(f"Ошибка {resp.status}: {await resp.text()}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
