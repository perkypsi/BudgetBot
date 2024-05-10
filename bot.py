import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters.command import Command, CommandObject
from config_reader import config
from income import income, keyboardsIncome
from category import category
from outcome import outcome
from debt import debt
from person import person
from aiogram.fsm.context import FSMContext
from utils import check_chat_id, CHATS

router = Router()
bot = Bot(token=config.bot_token.get_secret_value())
CHATS += config.chat_ids

@router.message(Command("cancel"))
@check_chat_id(CHATS)
async def cmd_cancel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    messages_to_delete = data.get('messages_to_delete')
    if messages_to_delete is not None:
        await message.bot.delete_messages(message.chat.id, messages_to_delete)
    await state.clear()
    await message.answer("Цепочка действий прервана")

@router.message(Command("info"))
@check_chat_id(CHATS)
async def cmd_cancel(message: types.Message, state: FSMContext):
    data = await state.get_data()
    messages_to_delete = data.get('messages_to_delete')
    if messages_to_delete is not None:
        await message.bot.delete_messages(message.chat.id, messages_to_delete)
    await state.clear()
    await message.answer("""Финансовый бот, доступны следующте команды:
/info - получение доступных команд
/cancel - остановка существующих цепочек действий
/income <volume> <DD.MM.YYYY> <description> - регистрация дохода
/outcome <volume> <DD.MM.YYYY> <description> - регистрация расхода
/table - получение excel таблицы со всеми финансовыми данным
/delincome - удалить запись о доходе
/deloutcome - удалить запись о расходе
Долги:
/debt - регистрация долга
/paydebt - закрыть долг
/deldebt - удалить долг
Категории:
/addCategory - добавить категорию
/printCategory - посмотреть все категории
/delCategory - удалить категорию
Люди:
/person - добавить человека
/printpersons - Показать последних 10 человек
/delperson - удалить человека
""")

@router.message(Command("start"))
@check_chat_id(CHATS)
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

async def main():
    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher()

    dp.include_routers(router, income.router, outcome.router, keyboardsIncome.router, category.router,
                       person.router, debt.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
