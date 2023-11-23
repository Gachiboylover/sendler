import requests
from aiogram import Bot, types
from environs import Env


env = Env()
env.read_env()

BOT_TOKEN = env("BOT_TOKEN")
UNRAR_tool = env("UnRAR.exe")
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)


