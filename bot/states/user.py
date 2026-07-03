from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    order_section = State()
