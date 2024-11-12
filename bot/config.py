from os import getenv
from dotenv import load_dotenv

load_dotenv("/TaskManagment/.env.example")

TELEGRAM_BOT_TOKEN = getenv('TELEGRAM_BOT_TOKEN')

DATABASE_CONNECTION_STRING = getenv(str('DATABASE_CONNECTION_STRING'))

SECRET_KEY = getenv("SECRET_KEY")

API_HASH = getenv('API_HASH')

API_ID = getenv('API_ID')






