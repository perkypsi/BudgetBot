from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, CallbackQuery, BufferedInputFile, InputFile, FSInputFile
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from utils import check_chat_id, CHATS
import io

from models import printCategory, addIncome, create_transaction_table, getIncomes, delIncome

router = Router()

class incomeRegister(StatesGroup):
    description_transaction= State()
    date_transaction = State()
    volume_transaction = State()
    category_transaction = State()

@router.message(Command("income"))
@check_chat_id(CHATS)
async def cmd_income(
        message: Message,
        command: CommandObject,
        state: FSMContext
):
    builder = InlineKeyboardBuilder()

    if command.args is None:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/income <volume> <DD.MM.YYYY> <description>"
        )
        await state.clear()
        return

    try:
        volume, date, description = command.args.split(" ", maxsplit=2)
        volume = float(volume)
        date = datetime.strptime(date, '%d.%m.%Y')

    except ValueError:
        await message.answer(
            "Ошибка: неправильный формат команды. Пример:\n"
            "/income <volume> <DD.MM.YYYY> <description>"
        )
        await state.clear()
        return
    
    categories = printCategory()

    if len(categories) == 0:
        await message.answer(
            "Список категорий пуст, доход не будет добавлен. Сначала добавьте категорию"
        )
        await state.clear()
    else:
        for category in categories:
                builder.add(InlineKeyboardButton(
                    text=category.name,
                    callback_data=f'choiceIncome_{category.name}')
                )
        await message.answer(text="Выберите категорию",
            reply_markup=builder.as_markup()
        )

    await state.set_state(incomeRegister.description_transaction)
    await state.update_data(description=description, date=date, volume=volume)
    await state.set_state(incomeRegister.category_transaction)

@router.message(Command("table"))
@check_chat_id(CHATS)
async def send_transaction_table(message: Message, command: CommandObject):
    docs = BufferedInputFile(file=create_transaction_table().getbuffer(), filename='finance.xlsx')
    await message.answer_document(docs, caption='Все существующие финансовые данные')

@router.message(Command("delincome"))
async def del_income(message: Message, command: CommandObject):
    incomes = getIncomes()
    builder = InlineKeyboardBuilder()
    if incomes.count() > 0:
        for income in incomes:
                    builder.add(InlineKeyboardButton(
                        text=f'{income.description} {income.volume:.2f}',
                        callback_data=f'delIncome_{income.id}')
                    )
        await message.answer(text="Выберите доход",
            reply_markup=builder.as_markup()
        )
    else:
         await message.reply(text="Список доходов пуст")


@router.callback_query(F.data.startswith("choiceIncome_"))
async def register_income_category_callback(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    await callback.message.answer(
        f"Транзакция зарегистрирована"
    )
    data = await state.get_data()
    addIncome(description=data['description'], date=data['date'], volume=data['volume'], category=data['category'])
    await state.clear()

@router.callback_query(F.data.startswith("delIncome_"))
async def delete_income_callback(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    id_ = callback.data.split("_")[1]
    await callback.message.answer(
        f"Транзакция удалена"
    )
    delIncome(id=id_)
    await state.clear()
