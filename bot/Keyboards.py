from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.types import ReplyKeyboardMarkup, KeyboardButton


class BotKeyboards:

    def __init__(self):
        pass

    def welcome_keyboard(self):

        keyboard = ReplyKeyboardMarkup([
            [KeyboardButton("Регистрация")],
            [KeyboardButton("Помощь")],
        ], resize_keyboard=True)

        return keyboard

    def registration(self, action):

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

    def main_menu(self):

        keyboard = ReplyKeyboardMarkup([

            [KeyboardButton("Создать задачу")],
            [KeyboardButton("Просмотр задач")],
            [KeyboardButton("Обновление задачи")],
            [KeyboardButton("Удаление задачи")],
            [KeyboardButton("Мой профиль")]

        ], resize_keyboard=True)

        return keyboard

    def create_task(self, action):

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

    def task_state(self):

        keyboard = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("Выполненные", callback_data="active_tasks")],
                [InlineKeyboardButton("Не выполненные", callback_data="not_active_tasks")],
                [InlineKeyboardButton("Отмена", callback_data="cancel_viewing")]
            ]

        )
        return keyboard

    def task_viewer(self, tasks, slides, task_state):

        buttons = [[InlineKeyboardButton(button[1], callback_data=f"Задача {button[0]}")] for button in tasks]

        next_button = InlineKeyboardButton("»", callback_data=f"»{task_state}")

        previous_button = InlineKeyboardButton("«", callback_data=f"«{task_state}")

        task_menu = InlineKeyboardButton("Назад", callback_data="task_menu")

        if slides == "no_pages":

            buttons.append([task_menu])

        elif slides == "first_page":

            buttons.append([task_menu])
            buttons.append([next_button])

        elif slides == "last_page":

            buttons.append([task_menu])
            buttons.append([previous_button])

        else:

            buttons.append([task_menu])
            buttons.append([previous_button, next_button])

        keyboard = InlineKeyboardMarkup(buttons)

        return keyboard
