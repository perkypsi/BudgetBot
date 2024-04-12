from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

# def get_yes_no_kb() -> ReplyKeyboardMarkup:
#     buttons = [
#         [
#             InlineKeyboardButton(text="-1", callback_data="num_decr"),
#             InlineKeyboardButton(text="+1", callback_data="num_incr")
#         ],
#         [InlineKeyboardButton(text="Подтвердить", callback_data="num_finish")]
#     ]
#     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
#     return keyboard

router = Router()  # [1]

class incomeRegister(StatesGroup):
    description_transaction= State()
    date_transaction = State()
    volume_transaction = State()
    account_transaction = State()
    category_transaction = State()

# @router.message(Command("start"))  # [2]
# async def cmd_start(message: Message):
#     await message.answer(
#         "Вы довольны своей работой?",
#         reply_markup=get_yes_no_kb()
#     )

# @router.message(F.text.lower() == "да")
# async def answer_yes(message: Message):
#     await message.answer(
#         "Это здорово!",
#         reply_markup=ReplyKeyboardRemove()
#     )

# @router.message(F.text.lower() == "нет")
# async def answer_no(message: Message):
#     await message.answer(
#         "Жаль...",
#         reply_markup=ReplyKeyboardRemove()
#     )

@router.message(Command("income"))
async def cmd_income(
        message: Message,
        command: CommandObject,
        state: FSMContext
):
    # Если не переданы никакие аргументы, то
    # command.args будет None
    if command.args is None:
        await state.set_state(incomeRegister.description_transaction)
    
    # Пробуем разделить аргументы на две части по первому встречному пробелу
    try:
        volume, date, description = command.args.split(" ", maxsplit=2)
        volume = float(volume)
        date = datetime.strptime(date, '%d.%m.%Y')
    
    # Если получилось меньше двух частей, вылетит ValueError
    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/income <volume> <DD.MM.YYYY> <description>"
        )
        await state.clear()
        return
    
    await state.set_state(incomeRegister.description_transaction)
    await state.update_data(description=description, date=date, volume=volume)
    await state.set_state(incomeRegister.account_transaction)

    # await message.answer(
    #     "Зарегистрирована транзакция!\n"
    #     f"Объем: {volume}\n"
    #     f"Дата: {date}\n"
    #     f"Описание: {description}"
    # )

@router.message(incomeRegister.account_transaction)
async def chosen_account(message: Message, state: FSMContext):
    await message.answer(
        text="Спасибо. Теперь, пожалуйста, выберите размер порции:",
    )
    await state.set_state(OrderFood.choosing_food_size)