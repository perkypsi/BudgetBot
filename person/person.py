from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardButton, InlineKeyboardBuilder
from utils import check_chat_id, CHATS

from models import addPerson, getPersons, delPerson

router = Router()

class PersonRegister(StatesGroup):
    last_name= State()
    first_name = State()
    patronymic = State()
    username = State()
    description = State()

@router.message(Command("person"))
@check_chat_id(CHATS)
async def cmd_person(
        message: Message,
        command: CommandObject,
        state: FSMContext
):
    await state.update_data(messages_to_delete=[])
    smessage = await message.answer(
        "Введите фамилию человека"
    )
    data = await state.get_data()
    messages_to_delete = data['messages_to_delete']
    messages_to_delete.append(smessage.message_id)
    messages_to_delete.append(message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)

    await state.set_state(PersonRegister.last_name)
    
@router.message(PersonRegister.last_name)
@check_chat_id(CHATS)
async def choice_last_name(message: Message, state: FSMContext):
    await state.update_data(last_name=message.text)
    smessage = await message.answer(
        "Введите имя человека"
    )
    
    data = await state.get_data()
    messages_to_delete = data['messages_to_delete']
    messages_to_delete.append(smessage.message_id)
    messages_to_delete.append(message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(PersonRegister.first_name)

@router.message(PersonRegister.first_name)
@check_chat_id(CHATS)
async def choice_first_name(message: Message, state: FSMContext):
    await state.update_data(first_name=message.text)
    smessage = await message.answer(
        "Введите отчество человека, если это необходимо"
    )
    data = await state.get_data()
    messages_to_delete = data['messages_to_delete']
    messages_to_delete.append(smessage.message_id)
    messages_to_delete.append(message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(PersonRegister.patronymic)

@router.message(PersonRegister.patronymic)
@check_chat_id(CHATS)
async def choice_patronymic(message: Message, state: FSMContext):
    await state.update_data(patronymic=message.text)
    smessage = await message.answer(
        "Введите имя пользователя"
    )
    data = await state.get_data()
    messages_to_delete = data['messages_to_delete']
    messages_to_delete.append(smessage.message_id)
    messages_to_delete.append(message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(PersonRegister.username)

@router.message(PersonRegister.username)
@check_chat_id(CHATS)
async def choice_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    smessage = await message.answer(
        "Введите описание человека"
    )
    data = await state.get_data()
    messages_to_delete = data['messages_to_delete']
    messages_to_delete.append(smessage.message_id)
    messages_to_delete.append(message.message_id)
    await state.update_data(messages_to_delete=messages_to_delete)
    await state.set_state(PersonRegister.description)

@router.message(PersonRegister.description)
@check_chat_id(CHATS)
async def choice_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    data = await state.get_data()
    addPerson(username=data['username'], last_name=data['last_name'], first_name=data['first_name'], patronymic=data['patronymic'], description=data['description'])
    await message.answer(
        "Человек добавлен в БД"
    )
    data = await state.get_data()
    messages_to_delete = data['messages_to_delete']
    messages_to_delete.append(message.message_id)
    await state.clear()
    await message.bot.delete_messages(message.chat.id, messages_to_delete)

@router.message(Command("delperson"))
@check_chat_id(CHATS)
async def del_person(message: Message, command: CommandObject):
    persons = getPersons()
    builder = InlineKeyboardBuilder()
    if persons.count() > 0:
        for person in persons:
                    builder.add(InlineKeyboardButton(
                        text=f'{person.last_name} {person.first_name} {person.username}',
                        callback_data=f'delPerson_{person.id}')
                    )
        await message.answer(text="Выберите человека",
            reply_markup=builder.as_markup()
        )
    else:
         await message.reply(text="Список людей пуст")


@router.message(Command("printpersons"))
@check_chat_id(CHATS)
async def printPersons(message: Message):
    
    persons = getPersons()
    if persons.count() > 0:
        await message.answer(
            text='Зарегистрированные люди:\n' + '\n'.join([f'{x.username} -- {x.last_name} {x.first_name}' for x in persons])
        )
    else:
        await message.answer(
            text='Список людей пуст'
        )


@router.callback_query(F.data.startswith("delPerson_"))
async def delete_income_callback(callback: CallbackQuery, state: FSMContext):
    await callback.bot.delete_message(chat_id=callback.message.chat.id, message_id=callback.message.message_id)
    id_ = callback.data.split("_")[1]
    await callback.message.answer(
        f"Человек удален"
    )
    delPerson(id=id_)
    await state.clear()