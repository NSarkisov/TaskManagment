import json
import sqlite3 as sl
from pyrogram import Client, filters, types
from pyrogram.enums import ParseMode
from pprint import pprint
import asyncio
import Keyboards
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from transitions import Machine

""" 
    Задачи на вторник:
    - Переделать бота используя FSM, бот готов только редактирования
    - Приступить к написанию архитектурной схемы
    - не забыть про типизацию (duck typing) и докстринги
    - Если получиться быстрее начать делать задачи Среды
    
    Задачи на среду:
    - Сборка проекта в docker
    - Провести обзор выбранных технологий и инструментов
    - Всю необходимую информацию записать в ReadME
    - Создать структуру базы данных (чертёж, таблица Миро, DrawIO) больше к DrawIO
    - Описать каждый запрос к базе данных
    - Инструкции по развертыванию и запуску бота.
    - Протестировать на виртуальной машине (тип вм желательно серверное (Windows Srv или Linux))
     работу развернутого бота (Больше Win Srv)    

"""

with open("../Config/config.json") as file:
    config = json.load(file)
    token = config.get("telegram_token")
    api_id = config.get("api_id")
    api_hash = config.get("api_hash")
    database = config.get("database_path")

with open("../db/sql_queries.json") as file:
    config = json.load(file)
    queries = config.get("queries")

with open("../db/texts.json", "r", encoding='utf-8') as file:
    config = json.load(file)
    texts_dict = config.get("texts")

con = sl.connect(database, check_same_thread=False)

app = Client(name='Task_bot', api_id=api_id, api_hash=api_hash, bot_token=token, parse_mode=ParseMode.HTML)

bot_keyboards = Keyboards.BotKeyboards()

buffer = {
    "messages_for_edit": {},
    "creating_task": {},
    "task_groups": {}

}  # telegram_id: message.id


async def task_view(bot: Client, telegram_id, column, task_state):
    with con:

        tasks = con.execute(queries["searching_active_tasks"], [task_state, telegram_id]).fetchall()

        groups = (len(tasks) + 4) // 5

        last_group = len(tasks) - (len(tasks) % 5)

        if column == 0 and groups == 1:

            keyboard = bot_keyboards.task_viewer(tasks[:5], "no_pages", task_state)

        elif column == 0 and groups > 1:

            keyboard = bot_keyboards.task_viewer(tasks[:5], "first_page", task_state)

        elif column == groups - 1 and groups > 1:

            keyboard = bot_keyboards.task_viewer(tasks[last_group:], "last_page", task_state)

        elif groups != column:
            keyboard = bot_keyboards.task_viewer(tasks[column * 5:(column + 1) * 5], "both", task_state)

    message_for_edit = await bot.edit_message_text(telegram_id, buffer["messages_for_edit"][telegram_id],
                                                   "📝Список ваших задач📝 : ", reply_markup=keyboard)

    buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})


@app.on_message(filters.command('start') & filters.private)
async def start(bot: Client, message: types.Message):
    telegram_id, telegram_link = message.from_user.id, "@" + message.from_user.username

    with con:

        user_exists = con.execute(queries["searching_user"], [telegram_id]).fetchall()

        if not user_exists:

            con.execute(queries["adding_user"], [telegram_id, telegram_link])

            registration_keyboard = bot_keyboards.welcome_keyboard()

            await bot.send_message(message.chat.id, ''.join(texts_dict['/start']), reply_markup=registration_keyboard)

        else:

            user_login = con.execute(queries["users_login"], [telegram_id]).fetchall()[0][0]

            main_menu_keyboard = bot_keyboards.main_menu()

            greetings_text = (f"{texts_dict['for_registered'][0]} <b><i>{user_login}</i></b>"
                              f"\n{texts_dict['for_registered'][1]}")

            await bot.send_message(message.chat.id, greetings_text, reply_markup=main_menu_keyboard)


@app.on_message(filters.text & filters.private & filters.regex(r"^Регистрация$|^Помощь$"))
async def registration(bot: Client, message: types.Message):
    if message.text == "Регистрация":
        telegram_id = message.from_user.id

        registration_keyboard = bot_keyboards.registration("Name")

        message_for_edit = await bot.send_message(message.chat.id, ''.join(texts_dict['Registration']),
                                                  reply_markup=registration_keyboard)

        buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

    if message.text == "Помощь$":
        print("")  # TO DO


@app.on_message(filters.text & filters.private & filters.regex(r"^Создать задачу$"))
async def create_task(bot: Client, message: types.Message):
    telegram_id = message.from_user.id

    if telegram_id in buffer["messages_for_edit"].keys():
        await bot.delete_messages(telegram_id, buffer["messages_for_edit"][telegram_id])

    with con:
        check_state = con.execute(queries["check_status"], [telegram_id]).fetchall()[0][0]

        if check_state == "Зарегистрирован":
            keyboard = bot_keyboards.create_task("Новая задача")

            message_for_edit = await bot.send_message(message.chat.id,
                                                      ''.join(texts_dict["Task_create"]),
                                                      reply_markup=keyboard)

            buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})


@app.on_message(filters.text & filters.private & filters.regex(r"^Просмотр задач$"))
async def task_overview(bot: Client, message: types.Message):
    telegram_id = message.from_user.id

    if telegram_id in buffer["messages_for_edit"].keys():
        await bot.delete_messages(telegram_id, buffer["messages_for_edit"][telegram_id])

    with con:
        check_state = con.execute(queries["check_status"], [telegram_id]).fetchall()[0][0]

        if check_state == "Зарегистрирован":

            if message.text == "Просмотр задач":

                tasks_in_db = con.execute(queries["searching_for_tasks"], [telegram_id]).fetchall()

                if tasks_in_db:

                    keyboard = bot_keyboards.task_state()

                    message_for_edit = await bot.send_message(message.chat.id,
                                                              texts_dict["Task_view"][1], reply_markup=keyboard)

                    buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

                else:

                    await bot.send_message(message.chat.id, texts_dict["Task_view"][0])


@app.on_message(filters.text & filters.private & filters.regex(r"^Мой профиль$"))
async def profile(bot: Client, message: types.Message):
    telegram_id = message.from_user.id

    if  telegram_id in buffer["messages_for_edit"].keys():

        await bot.delete_messages(telegram_id, buffer["messages_for_edit"][telegram_id])

    with con:
        check_state = con.execute(queries["check_status"], [telegram_id]).fetchall()[0][0]

        if check_state == "Зарегистрирован":
            name_login = con.execute(queries["users_name_login"], [telegram_id]).fetchall()[0]

            name = name_login[0]

            login = name_login[1]

            profile_text = (f"{texts_dict['Profile'][0]}\n\nВаше имя: <b><i>{name}</i></b>\n\n"
                            f"Ваш логин: <b><i>{login}</i></b>\n\n{texts_dict['Profile'][0]}")

            keyboard = bot_keyboards.profile()

            message_for_edit = await bot.send_message(telegram_id, profile_text, reply_markup=keyboard)

            buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})


@app.on_message(filters.text & filters.private)
async def text(bot: Client, message: types.Message):

    telegram_id = message.from_user.id

    with con:

        user_exists = con.execute(queries["searching_user"], [telegram_id]).fetchall()

        if user_exists:

            check_state = con.execute(queries["check_status"], [telegram_id]).fetchall()[0][0]

            check_task_process = con.execute(queries["check_task_process"], [telegram_id]).fetchall()[0][0]

        if user_exists and check_state != "Зарегистрирован":

            if check_state == "Регистрация":
                registration_keyboard = bot_keyboards.registration("Name")

                await bot.delete_messages(message.chat.id, buffer["messages_for_edit"][telegram_id])

                message_for_edit = await bot.send_message(message.chat.id, ''.join(texts_dict['Registration']),
                                                          reply_markup=registration_keyboard)

                buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

            if check_state == "Ввод имени":

                login_button = bot_keyboards.registration("Login")

                user_name = con.execute(queries["find_name"], [telegram_id]).fetchall()[0][0]

                if user_name is None:

                    con.execute(queries["name_write"], [message.text, telegram_id])

                    message_for_edit = await bot.send_message(message.chat.id,
                                                              f"Отлично {message.text}!\n" + texts_dict['Login'],
                                                              reply_markup=login_button
                                                              )
                else:

                    await bot.delete_messages(message.chat.id, buffer["messages_for_edit"][telegram_id])

                    message_for_edit = await bot.send_message(message.chat.id,
                                                              f"Отлично {user_name}!\n" + texts_dict['Login'],
                                                              reply_markup=login_button
                                                              )

                buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

            if check_state == "Ввод Логина":
                con.execute(queries['login_write'], [message.text, telegram_id])

                con.execute(queries["state_update"], ["Зарегистрирован", telegram_id])

                user_name = con.execute(queries["find_name"], [telegram_id]).fetchall()[0][0]

                menu_keyboard = bot_keyboards.main_menu()

                await bot.send_message(message.chat.id,
                                       texts_dict["Welcome"][0] + " " + user_name + "!\n" + ''.join(
                                           texts_dict["Welcome"][1:]),
                                       reply_markup=menu_keyboard)

            if check_state == "Ввод нового имени":
                name = message.text

                con.execute(queries["name_update"], [name, telegram_id])

                login = con.execute(queries["users_login"], [telegram_id]).fetchall()[0][0]

                profile_text = (f"{texts_dict['Profile'][0]}\n\nВаше имя: <b><i>{name}</i></b>\n\n"
                                f"Ваш логин: <b><i>{login}</i></b>\n\n{texts_dict['Profile'][0]}")

                keyboard = bot_keyboards.profile()

                message_for_edit = await bot.send_message(telegram_id, profile_text, reply_markup=keyboard)

                buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

                con.execute(queries["state_update"], ["Зарегистрирован", telegram_id])

            if check_state == "Ввод нового логина":
                login = message.text

                con.execute(queries["login_update"], [login, telegram_id])

                name = con.execute(queries["users_name"], [telegram_id]).fetchall()[0][0]

                profile_text = (f"{texts_dict['Profile'][0]}\n\nВаше имя: <b><i>{name}</i></b>\n\n"
                                f"Ваш логин: <b><i>{login}</i></b>\n\n{texts_dict['Profile'][0]}")

                keyboard = bot_keyboards.profile()

                message_for_edit = await bot.send_message(telegram_id, profile_text, reply_markup=keyboard)

                buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

                con.execute(queries["state_update"], ["Зарегистрирован", telegram_id])

        if user_exists and check_task_process == "Ввод имени":
            user_id = con.execute(queries["user_id"], [telegram_id]).fetchall()[0][0]

            keyboard = bot_keyboards.create_task("Описание задачи")

            message_for_edit = await bot.send_message(message.chat.id,
                                                      texts_dict["Task_name"][0] + message.text +
                                                      ''.join(texts_dict["Task_name"][1:]),
                                                      reply_markup=keyboard)

            buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

            buffer["creating_task"].update({telegram_id: [user_id, message.text]})

        if user_exists and check_task_process == "Ввод описания":
            con.execute(queries["task_status_update"], ["Не создаёт", telegram_id])

            task_name = buffer["creating_task"][telegram_id][1]

            task_description = message.text

            keyboard = bot_keyboards.create_task("Подтверждение создания")

            buffer["creating_task"][telegram_id].append(message.text)

            message_for_edit = await bot.send_message(message.chat.id,
                                                      texts_dict["Check_Task"][0] + task_name + "\n" + task_description
                                                      + "\n" + texts_dict["Check_Task"][1],
                                                      reply_markup=keyboard)

            buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})


@app.on_callback_query()
async def callback_query(bot: Client, call: types.CallbackQuery):
    chat_id = call.message.chat.id
    # message_id = call.message.id
    button_name = call.data

    if button_name == "Name":
        message_for_edit = await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                                       "Введите Имя:", reply_markup=None)

        buffer["messages_for_edit"].update({chat_id: message_for_edit.id})

        with con:
            con.execute(queries["state_update"], ["Ввод имени", chat_id])

    if button_name == "Login":
        message_for_edit = await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                                       "Введите Логин:", reply_markup=None)

        buffer["messages_for_edit"].update({chat_id: message_for_edit.id})

        with con:
            con.execute(queries["state_update"], ["Ввод Логина", chat_id])

    if button_name == "change_name":
        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id], "Введите новое имя: ",
                                    reply_markup=None)
        with con:
            con.execute(queries["state_update"], ["Ввод нового имени", chat_id])

    if button_name == "change_login":
        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id], "Введите новый логин: ",
                                    reply_markup=None)
        with con:
            con.execute(queries["state_update"], ["Ввод нового логина", chat_id])

    if button_name == "cancel_profile":

        await bot.delete_messages(chat_id, buffer["messages_for_edit"][chat_id])

    if button_name == "task_name":
        with con:
            con.execute(queries["task_status_update"], ["Ввод имени", chat_id])

        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                    "Введите название задачи: ")

    if button_name == "task_description":
        with con:
            con.execute(queries["task_status_update"], ["Ввод описания", chat_id])

        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                    "Введите описание задачи: ")

    if button_name == "task_accept":
        user_id = buffer["creating_task"][chat_id][0]
        task_name = buffer["creating_task"][chat_id][1]
        task_description = buffer["creating_task"][chat_id][2]

        with con:
            con.execute(queries["create_task"], [user_id, task_name, task_description])

        buffer["creating_task"].pop(chat_id)

        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                    f"Ваша зада {task_name} успешно создана.\n"
                                    f"Посмотреть задачу вы можете в навигационном меню 'Просмотр задач'")

    if button_name == "Cancel_task_creating":

        with con:

            con.execute(queries["task_status_update"], ["Не создаёт", chat_id])

        if chat_id in buffer["creating_task"].keys():
            buffer["creating_task"].pop(chat_id)

        await bot.delete_messages(chat_id, buffer["messages_for_edit"][chat_id])

    if button_name == "active_tasks":

        with con:

            tasks = con.execute(queries["searching_active_tasks"], ["Не выполнена", chat_id]).fetchall()

            if tasks:

                buffer["task_groups"].update({chat_id: {"active_slide": 0, "task_state": "Не выполнена"}})

                await task_view(bot, chat_id, column=0, task_state="Не выполнена")

            else:

                state_text = f"{texts_dict['tasks_left'][0]} активных {texts_dict['tasks_left'][1]}"

                keyboard = bot_keyboards.task_menu()

                await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                            state_text, reply_markup=keyboard)

    if button_name == "not_active_tasks":

        with con:

            tasks = con.execute(queries["searching_active_tasks"], ["Выполнена", chat_id]).fetchall()

            if tasks:

                buffer["task_groups"].update({chat_id: {"active_slide": 0, "task_state": "Выполнена"}})

                await task_view(bot, chat_id, column=0, task_state="Выполнена")

            else:

                state_text = f"{texts_dict['tasks_left'][0]} не активных {texts_dict['tasks_left'][1]}"

                keyboard = bot_keyboards.task_menu()

                await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                            state_text, reply_markup=keyboard)

    if button_name == "task_menu":
        keyboard = bot_keyboards.task_state()

        message_for_edit = await bot.edit_message_text(chat_id,
                                                       buffer["messages_for_edit"][chat_id],
                                                       texts_dict["Task_view"][1],
                                                       reply_markup=keyboard)
        buffer["messages_for_edit"].update({chat_id: message_for_edit.id})

    if button_name.startswith("»"):
        task_state = button_name[1:]

        buffer["task_groups"][chat_id]["active_slide"] += 1

        column = buffer["task_groups"][chat_id]["active_slide"]

        await task_view(bot, chat_id, column=column, task_state=task_state)

    if button_name.startswith("«"):
        task_state = button_name[1:]

        buffer["task_groups"][chat_id]["active_slide"] -= 1

        column = buffer["task_groups"][chat_id]["active_slide"]

        await task_view(bot, chat_id, column=column, task_state=task_state)

    if button_name == "cancel_viewing":
        await bot.delete_messages(chat_id, buffer["messages_for_edit"][chat_id])

    if button_name.startswith("Задача"):

        task_id = button_name[7:]

        with con:
            task_info = con.execute(queries["task_description"], [task_id]).fetchall()[0]

            task_name = task_info[0]
            task_description = task_info[1]

            if buffer["task_groups"][chat_id]["task_state"] == "Не выполнена":

                task_state = texts_dict['task_info'][0]

            else:
                task_state = texts_dict['task_info'][1]

            task_text = (f"{task_state}<b><i>{task_name}</b></i>\n\n"
                         f"<b>{task_description}</b>\n\n{texts_dict['task_info'][2]}")

            keyboard = bot_keyboards.task_info(task_id)

            message_for_edit = await bot.edit_message_text(chat_id,
                                                           buffer["messages_for_edit"][chat_id],
                                                           text=task_text,
                                                           reply_markup=keyboard)

            buffer["messages_for_edit"].update({chat_id: message_for_edit.id})

    if button_name == "back_from_task_info":
        active_slide = buffer["task_groups"][chat_id]['active_slide']

        task_state = buffer["task_groups"][chat_id]['task_state']

        await task_view(bot, chat_id, column=active_slide, task_state=task_state)

    if button_name == "cancel_from_task_info":
        await bot.delete_messages(chat_id, buffer["messages_for_edit"][chat_id])

        buffer["task_groups"].pop(chat_id)

    if button_name.startswith("delete"):

        task_id = button_name[7:]

        task_state = buffer["task_groups"][chat_id]["task_state"]

        with con:

            task_name = con.execute(queries["task_name"], [task_id]).fetchall()[0][0]

            con.execute(queries["delete_task"], [task_id])

            task_left = con.execute(queries["searching_tasks_with_state"], [task_state, chat_id]).fetchall()

        await bot.answer_callback_query(call.id, f"Задача {task_name} удалена")

        if task_left:

            await task_view(bot, chat_id, column=0, task_state=task_state)

        else:

            if task_state == "Не выполнена":

                state_text = f"{texts_dict['tasks_left'][0]} активных {texts_dict['tasks_left'][1]}"

            else:

                state_text = f"{texts_dict['tasks_left'][0]} не активных {texts_dict['tasks_left'][1]}"

            keyboard = bot_keyboards.task_menu()

            await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                        state_text, reply_markup=keyboard)


    if button_name.startswith("change_state"):

        task_id = button_name[13:]

        with con:

            name_and_state = con.execute(queries["task_name_and_state"], [task_id]).fetchall()[0]

            task_name = name_and_state[0]

            task_state = name_and_state[1]

            if task_state == "Не выполнена":

                new_state = f"Задача {task_name} не активна"

                con.execute(queries["task_change_state"], ["Выполнена", task_id])

            else:

                new_state = f"Задача {task_name} активна"

                con.execute(queries["task_change_state"], ["Не выполнена", task_id])

            task_left = con.execute(queries["searching_tasks_with_state"], [task_state, chat_id]).fetchall()

        await bot.answer_callback_query(call.id, new_state)

        if task_left:

            await task_view(bot, chat_id, column=0, task_state=task_state)

        else:

            if task_state == "Не выполнена":

                state_text = f"{texts_dict['tasks_left'][0]} активных {texts_dict['tasks_left'][1]}"

            else:

                state_text = f"{texts_dict['tasks_left'][0]} не активных {texts_dict['tasks_left'][1]}"

            keyboard = bot_keyboards.task_menu()

            await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                        state_text, reply_markup=keyboard)


app.run()
