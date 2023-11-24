from aiogram import Bot
from aiogram.types import Message, BotCommand, BotCommandScopeDefault

async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='start',
            description='Старт.'
        ),
        BotCommand(
            command='help',
            description='Узнай функционал бота.'
        ),
        BotCommand(
            command='add_acc',
            description='Загрузи сессию.'
        ),
        BotCommand(
            command='enable_acc',
            description='Сделай сессию активной.'
        ),
        BotCommand(
            command='disable_acc',
            description='Выключи сессию.'
        ),
        BotCommand(
            command='pars_users',
            description='Спарсьте пользователей.'
        ),
        BotCommand(
            command='send_message',
            description='Отправьте сообщение.'
        ),
        BotCommand(
            command='users',
            description='Получите данные о всех пользователях в формате xlsx.'
        )
    ]
    await bot.set_my_commands(commands)
    print('[*] Bot pooling [*]')