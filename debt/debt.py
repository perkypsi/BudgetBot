from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove, ReplyKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardMarkup, InlineKeyboardBuilder
from aiogram.filters import Command, CommandObject, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from utils import check_chat_id, CHATS

from models import printPersons, addDebt, getPerson, getDebts, payDebt, delDebt

router = Router()

class DebtRegister(StatesGroup):
    choisen_debtor = State()
    choisen_recipient = State()
    choisen_volume = State()
    choisen_date = State()
    choisen_description = State()

async def update_persons(message: Message):
    builder = InlineKeyboardBuilder()
    persons = printPersons()
    for person in persons:
        builder.add(InlineKeyboardButton(
            text=person.last_name + " " + person.first_name,
            callback_data=f'choiceDebtor_{person.username}')
        )
    await message.edit_text(
        "Выберите того, кому должен",
        reply_markup=builder.as_markup()
    )

@router.message(Command("paydebt"))
@check_chat_id(CHATS)
async def cmd_paydebt(
        message: Message,
        command: CommandObject
):
    debts = getDebts()
    if debts.count() > 0:
        builder = InlineKeyboardBuilder()
        for debt in debts:
            builder.add(InlineKeyboardButton(
                text=f'Дата: {debt.date.strftime("%d.%m.%Y")} Сумма: {debt.volume:.2f} Описание: {debt.description}',
                callback_data=f'paydebt_{debt.id}')
            )
        await message.answer(
            "Выберите долг",
            reply_markup=builder.as_markup()
        )
    else:
        await message.answer(
            "На данный момент, активных долгов нет"
        )

@router.message(Command("debt"))
@check_chat_id(CHATS)
async def cmd_debt(
        message: Message,
        command: CommandObject,
        state: FSMContext
):
    builder = InlineKeyboardBuilder()
    persons = printPersons()
    for person in persons:
        builder.add(InlineKeyboardButton(
            text=person.last_name + " " + person.first_name,
            callback_data=f'choiceDebtor_{person.username}')
        )
    await message.answer(
        "Выберите должника",
        reply_markup=builder.as_markup()
    )
    await state.set_state(DebtRegister.choisen_recipient)

@router.message(DebtRegister.choisen_recipient)
@check_chat_id(CHATS)
async def choice_recipient(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    persons = printPersons()
    for person in persons:
        builder.add(InlineKeyboardButton(
            text=person.last_name + " " + person.first_name,
            callback_data=f'choiceRecipient_{person.username}')
        )
    await message.answer(
        "Выберите того, кому должен",
        reply_markup=builder.as_markup()
    )
    await state.set_state(DebtRegister.choisen_volume)

@router.message(DebtRegister.choisen_volume)
@check_chat_id(CHATS)
async def choice_volume(message: Message, state: FSMContext):
    await state.update_data(volume=float(message.text))
    await message.answer(
        "Введите дату начала долга"
    )
    await state.set_state(DebtRegister.choisen_date)

@router.message(DebtRegister.choisen_date)
@check_chat_id(CHATS)
async def choice_date(message: Message, state: FSMContext):
    date = datetime.strptime(message.text, '%d.%m.%Y')
    await state.update_data(date=date)
    await message.answer(
        "Введите описание долга"
    )
    await state.set_state(DebtRegister.choisen_description)

@router.message(DebtRegister.choisen_description)
@check_chat_id(CHATS)
async def choice_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    addDebt(data['debtor'], data['recipient'], data['volume'], data['date'], data['description'])
    await message.answer(
        "Долг зарегистрирован"
    )
    await state.clear()

@router.message(Command("deldebt"))
@check_chat_id(CHATS)
async def del_debt(message: Message, command: CommandObject):
    debts = getDebts()
    builder = InlineKeyboardBuilder()
    if debts.count() > 0:
        for debt in debts:
            builder.add(InlineKeyboardButton(
                text=f'{debt.description} {debt.volume:.2f}',
                callback_data=f'delDebt_{debt.id}')
            )
        await message.answer(text="Выберите долг",
            reply_markup=builder.as_markup()
        )
    else:
         await message.reply(text="Список долгов пуст")

@router.callback_query(F.data.startswith("choiceDebtor_"))
async def choice_debtor_callback(callback: CallbackQuery, state: FSMContext):
    debtor = callback.data.split("_")[1]
    person = getPerson(debtor)
    await state.update_data(debtor=person.id)
    await callback.answer("Выберите того, тко должен")
    await choice_recipient(message=callback.message, state=state)

@router.callback_query(F.data.startswith("choiceRecipient_"))
async def choice_recipient_callback(callback: CallbackQuery, state: FSMContext):
    recipient = callback.data.split("_")[1]
    person = getPerson(recipient)
    await state.update_data(recipient=person.id)
    await callback.message.answer(
        "Теперь введите сумму долга"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("paydebt_"))
async def choice_debt_callback(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    id_debt = callback.data.split("_")[1]
    person = payDebt(int(id_debt))
    await callback.message.answer(
        "Долг оплачен"
    )
    await callback.answer()

@router.callback_query(F.data.startswith("delDebt_"))
async def delete_income_callback(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    id_ = callback.data.split("_")[1]
    await callback.message.answer(
        f"Долг удален"
    )
    delDebt(id=id_)
    await state.clear()