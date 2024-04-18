from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from models import addCategory, printCategory, delCategory

router = Router()

class AddCategory(StatesGroup):
    name = State()
    final = State()

@router.message(Command("addCategory"))
async def cmd_income(
        message: Message,
        command: CommandObject,
        state: FSMContext
):
    await message.answer(
        text="Введите название категории",
    )

    await state.set_state(AddCategory.name)

@router.message(AddCategory.name)
async def chosen_account(message: Message, state: FSMContext):
    addCategory(message.text)
    await message.answer(
        text=f"Категория добавлена",
    )
    await state.clear()

@router.message(Command("printCategory"))
async def printCategories(message: Message):
    
    categories = printCategory()
    if len(categories) != 0:
        await message.answer(
            text='Доступные категории:\n' + '\n'.join([x.name for x in categories])
        )
    else:
        await message.answer(
            text='Список категорий пуст'
        )

@router.message(Command("delCategory"))
async def deleteCategory(message: Message):
    builder = InlineKeyboardBuilder()
    categories = printCategory()
    if len(categories) == 0:
        await message.answer(
            "Список категорий пуст",
            reply_markup=builder.as_markup()
        )
    else:
        for category in categories:
            builder.add(InlineKeyboardButton(
                text=category.name,
                callback_data=f'del_{category.name}')
            )
        await message.answer(
            "Выберите категорию для удаления",
            reply_markup=builder.as_markup()
        )

@router.callback_query(F.data.startswith("del_"))
async def delete_category_callback(callback: CallbackQuery):
    category = callback.data.split("_")[1]
    delCategory(category)
    await callback.message.answer(
        f"Категория {category} удалена"
    )