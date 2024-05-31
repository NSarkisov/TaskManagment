from pyrogram import Client, filters
from pyrogram.enums import ParseMode
from pyrogram.handlers import MessageHandler, CallbackQueryHandler
from bot import config
import handlers

"""
    В этом модуле реализован класс с экземпляром бота, инициализация подключения, сведения для подключения находятся
    в config.json, открытые в файле file_manager и импортированы в этот модуль, описаны и добавлены все обработчики,
    соответственно и сам запуск бота .
"""


class TaskBot:

    def __init__(self):
        self.app = Client(name='Task_bot', api_id=config.API_ID, api_hash=config.API_HASH,
                          bot_token=config.TELEGRAM_BOT_TOKEN, parse_mode=ParseMode.HTML)
        self.start_handler = MessageHandler(handlers.start, filters.command('start') & filters.private)
        self.registration_handler = MessageHandler(handlers.registration, filters.text & filters.private
                                                   & filters.regex(r"^Регистрация$|^Помощь$"))
        self.create_task_handler = MessageHandler(handlers.create_task,
                                                  filters.text & filters.private & filters.regex(r"^Создать задачу$"))
        self.task_overview_handler = MessageHandler(handlers.task_overview,
                                                    filters.text & filters.private & filters.regex(r"^Просмотр задач$"))
        self.profile_handler = MessageHandler(handlers.profile,
                                              filters.text & filters.private & filters.regex(r"^Мой профиль$"))
        self.text_handler = MessageHandler(handlers.text, filters.text & filters.private)
        self.callback_query_handler = CallbackQueryHandler(handlers.callback_query)

    def run(self):
        self.app.add_handler(self.start_handler)
        self.app.add_handler(self.registration_handler)
        self.app.add_handler(self.create_task_handler)
        self.app.add_handler(self.task_overview_handler)
        self.app.add_handler(self.profile_handler)
        self.app.add_handler(self.text_handler)
        self.app.add_handler(self.callback_query_handler)

        self.app.run()


app = TaskBot()
app.run()
