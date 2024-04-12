import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command, CommandObject
from config_reader import config
from income import income, keyboardsIncome

# # Хэндлер на команду /start
# @dp.message(Command("start"))
# async def cmd_start(message: types.Message):
#     await message.answer("Hello!")

# @dp.message(Command("settimer"))
# async def cmd_settimer(
#         message: types.Message,
#         command: CommandObject
# ):
#     # Если не переданы никакие аргументы, то
#     # command.args будет None
#     if command.args is None:
#         await message.answer(
#             "Ошибка: не переданы аргументы"
#         )
#         return
#     # Пробуем разделить аргументы на две части по первому встречному пробелу
#     try:
#         delay_time, text_to_send = command.args.split(" ", maxsplit=1)
#     # Если получилось меньше двух частей, вылетит ValueError
#     except ValueError:
#         await message.answer(
#             "Ошибка: неправильный формат команды. Пример:\n"
#             "/settimer <time> <message>"
#         )
#         return
#     await message.answer(
#         "Таймер добавлен!\n"
#         f"Время: {delay_time}\n"
#         f"Текст: {text_to_send}"
#     )

# Запуск процесса поллинга новых апдейтов
async def main():
    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(level=logging.INFO)

    # Объект бота
    bot = Bot(token=config.bot_token.get_secret_value())

    # Диспетчер
    dp = Dispatcher()

    dp.include_routers(income.router, keyboardsIncome.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
