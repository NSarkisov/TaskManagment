from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton

"""
    В этом модуле создаётся класс с методами создания объектов различных клавиатур, таких как
    ReplyKeyboardMarkup и InlineKeyboardMarkup, каждый из методов класса возвращает клавиатуру,
    экземпляр класса создается в файле handlers.py 
"""
class BotKeyboards:

    def __init__(self):
        pass

    def welcome_keyboard(self) -> ReplyKeyboardMarkup:

        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("Регистрация")],
            [KeyboardButton("Помощь")],
        ], resize_keyboard=True)

        return keyboard

    def registration(self, action) -> InlineKeyboardMarkup:

        if action == "Name":
            name_button = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Имя", callback_data="Name")
                    ]
                ]
            )
            return name_button

        if action == "Login":
            login_button = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Логин", callback_data="Login")
                    ]
                ]
            )
            return login_button


    def profile(self) -> InlineKeyboardMarkup:

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Имя", callback_data="change_name"),
                    InlineKeyboardButton("Логин", callback_data="change_login"),
                    InlineKeyboardButton("Отмена", callback_data="cancel_profile"),

                ]
            ]
        )

        return keyboard

    def main_menu(self) -> ReplyKeyboardMarkup:

        keyboard = ReplyKeyboardMarkup([

            [KeyboardButton("Создать задачу")],
            [KeyboardButton("Просмотр задач")],
            [KeyboardButton("Мой профиль")]

        ], resize_keyboard=True)

        return keyboard

    def create_task(self, action) -> InlineKeyboardMarkup:

        if action == "Новая задача":
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Имя задачи", callback_data="task_name"),
                        InlineKeyboardButton("Отмена", callback_data="Cancel_task_creating")
                    ]
                ]
            )
            return keyboard

        if action == "Описание задачи":
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Описание задачи", callback_data="task_description"),
                        InlineKeyboardButton("Отмена", callback_data="Cancel_task_creating")
                    ]
                ]
            )
            return keyboard

        if action == "Подтверждение создания":
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Подтвердить", callback_data="task_accept"),
                        InlineKeyboardButton("Отмена", callback_data="Cancel_task_creating")
                    ]
                ]
            )
            return keyboard

    def task_state(self) -> InlineKeyboardMarkup:

        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Активные", callback_data="active_tasks")],
                [InlineKeyboardButton("Не активные", callback_data="not_active_tasks")],
                [InlineKeyboardButton("Отмена", callback_data="cancel_viewing")]
            ]

        )
        return keyboard

    def task_menu(self) -> InlineKeyboardMarkup:

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Назад", callback_data="task_menu")
                ]
            ]
        )

        return keyboard

    def task_viewer(self, tasks, slides, task_state) -> InlineKeyboardMarkup:

        buttons = [[InlineKeyboardButton(button[1], callback_data=f"Задача {button[0]}")] for button in tasks]

        next_button = InlineKeyboardButton("»", callback_data=f"»{task_state}")

        previous_button = InlineKeyboardButton("«", callback_data=f"«{task_state}")

        task_menu = InlineKeyboardButton("Назад", callback_data="task_menu")

        if slides == "no_pages":

            buttons.append([task_menu])

        elif slides == "first_page":

            buttons.append([task_menu, next_button])

        elif slides == "last_page":

            buttons.append([previous_button, task_menu])

        else:

            buttons.append([previous_button, task_menu, next_button])

        keyboard = InlineKeyboardMarkup(buttons)

        return keyboard

    def task_info(self, task_id) -> InlineKeyboardMarkup:

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🗑️Удалить задачу", callback_data=f"delete {task_id}"),
                    InlineKeyboardButton("Сменить статус📝", callback_data=f"change_state {task_id}")
                ],
                [
                    InlineKeyboardButton("Назад", callback_data="back_from_task_info"),
                    InlineKeyboardButton("Отмена", callback_data="cancel_from_task_info")
                ]
            ]
        )

        return keyboard
