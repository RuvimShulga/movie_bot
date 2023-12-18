import requests
import json
import urllib
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '6894979902:AAEbC0-cA2Q-I29SZ5h53mGBmQwGB9ER7Ok'
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

token_kinopoisk = "2MPR2W5-BKP4DAB-KVCT0FC-6TXFK5Q"
url = "https://api.kinopoisk.dev/v1.4/movie/random?rating.imdb=7-10&lists=top250"  # Замени адрес сайта и путь до эндпоинта на свои

headers = {
    "X-API-KEY": f"{token_kinopoisk}"
}


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Hello!")


@dp.message_handler()
async def start_request(message: types.Message):
    response_list = get_movie()
    poster_url = response_list[0]
    response_str = "\n".join(map(str, response_list))

    urllib.request.urlretrieve(f"{poster_url}", "image.jpg")

    with open("image.jpg", "rb") as photo:
        await message.answer_photo(photo, response_str)

    os.remove("image.jpg")

def get_movie():
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        # Здесь можешь обрабатывать полученные данные
        
        print(json.dumps(data, indent=4))
        img = data["poster"]["url"]
        name = data["names"][0]["name"]
        rating = data["rating"]["imdb"]
        year = data["year"]
        description = data["description"]
        # trailers = json.dumps(data["videos"]["trailers"], indent=4)
        trailers_urls = []
        trailers = data["videos"]["trailers"]
        for trailer in trailers:
            trailers_urls.append(trailer["url"])

        print(name)
        print(rating)
        print(year)
        print(description)
        print(*trailers_urls, sep="\n")

        return [img, name, rating, year, description, trailers_urls]

    else:
        print(f"Ошибка {response.status_code}: {response.text}")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
