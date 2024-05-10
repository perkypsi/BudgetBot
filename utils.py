from functools import wraps
from aiogram import types

CHATS = [463762417]

def check_chat_id(chat_ids):
    def decorator(func):
        @wraps(func)
        async def wrapper(message: types.Message, *args, **kwargs):
            # Получаем id чата из сообщения
            chat_id = message.chat.id if message else None
            
            # Проверяем, есть ли id чата в списке допустимых
            if chat_id in chat_ids:
                # Если id чата есть в списке, выполняем функцию
                return await func(message, *args, **kwargs)
            else:
                # Если id чата нет в списке, отправляем отказ
                await message.answer("Извините, вы не имеете доступа к этой функции.")
        
        return wrapper
    return decorator