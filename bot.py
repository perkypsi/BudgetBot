import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters.command import Command, CommandObject
from config_reader import config
from income import income, keyboardsIncome
from category import category
from outcome import outcome

router = Router()
bot = Bot(token=config.bot_token.get_secret_value())

# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello!")

async def main():
    logging.basicConfig(level=logging.INFO)

    dp = Dispatcher()

    dp.include_routers(router, income.router, outcome.router, keyboardsIncome.router, category.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
