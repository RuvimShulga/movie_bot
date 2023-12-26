from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    username = State()


class Family(StatesGroup):
    family_name = State()


class Choice(StatesGroup):
    choice = State()


class Mode(StatesGroup):
    mode = State()
