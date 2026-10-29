from aiogram.fsm.state import State, StatesGroup


class Auth(StatesGroup):
    wait_link = State()


class Register(StatesGroup):
    platform = State()


class Renew(StatesGroup):
    tariff = State()
    days = State()
    target = State()
