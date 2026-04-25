from aiogram.fsm.state import State, StatesGroup

class AddHabitStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_description = State()
    waiting_for_reminder_time = State()
