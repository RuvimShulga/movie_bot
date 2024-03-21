from aiogram.fsm.state import StatesGroup, State

class Delete(StatesGroup):
    delete_movie = State()

class Config(StatesGroup):
    collections = State()

