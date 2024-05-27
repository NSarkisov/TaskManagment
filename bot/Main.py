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

        groups = buffer["task_groups"][telegram_id]["total_groups"]

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
            print("=============")  # TO_DO


@app.on_message(filters.text & filters.private & filters.regex(r"^Регистрация$|^Помощь$"))
async def registration(bot: Client, message: types.Message):
    if message.text == "Регистрация":
        telegram_id = message.from_user.id

        registration_keyboard = bot_keyboards.registration("Name")

        message_for_edit = await bot.send_message(message.chat.id, ''.join(texts_dict['Registration']),
                                                  reply_markup=registration_keyboard)

        buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})


@app.on_message(filters.text & filters.private & filters.regex(r"^Создать задачу$"))
async def registration(bot: Client, message: types.Message):
    telegram_id = message.from_user.id

    with con:
        check_state = con.execute(queries["check_status"], [telegram_id]).fetchall()[0][0]

        if check_state == "Зарегистрирован":
            keyboard = bot_keyboards.create_task("Новая задача")

            message_for_edit = await bot.send_message(message.chat.id,
                                                      ''.join(texts_dict["Task_create"]),
                                                      reply_markup=keyboard)

            buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})


@app.on_message(filters.text & filters.private & filters.regex(r"^Просмотр задач$"))
async def registration(bot: Client, message: types.Message):
    telegram_id = message.from_user.id

    with con:
        check_state = con.execute(queries["check_status"], [telegram_id]).fetchall()[0][0]

        if check_state == "Зарегистрирован":

            tasks_in_db = con.execute(queries["searching_for_tasks"], [telegram_id]).fetchall()
            #
            if tasks_in_db:

                keyboard = bot_keyboards.task_state()

                message_for_edit = await bot.send_message(message.chat.id,
                                                          texts_dict["Task_view"][1], reply_markup=keyboard)

                buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

            else:
                await bot.send_message(message.chat.id, texts_dict["Task_view"][0])


@app.on_message(filters.text & filters.private)
async def text(bot: Client, message: types.Message):
    telegram_id = message.from_user.id

    with con:

        user_exists = con.execute(queries["searching_user"], [telegram_id]).fetchall()

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

        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                    "Вы отменили создание задачи, воспользуйтесь навигационным меню")

    if button_name == "active_tasks":
        with con:
            tasks = con.execute(queries["searching_active_tasks"], ["Не выполнена", chat_id]).fetchall()

            groups = (len(tasks) + 4) // 5

            buffer["task_groups"].update({chat_id: {"total_groups": groups, "active_slide": 0}})

        await task_view(bot, chat_id, column=0, task_state="Не выполнена")

    if button_name == "not_active_tasks":
        with con:
            tasks = con.execute(queries["searching_active_tasks"], ["Выполнена", chat_id]).fetchall()

            groups = (len(tasks) + 4) // 5

            buffer["task_groups"].update({chat_id: {"total_groups": groups, "active_slide": 0}})

        await task_view(bot, chat_id, column=0, task_state="Выполнена")

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

    if button_name.startswith("Задача"):
        task_id = button_name[7:]
        print(task_id)


app.run()
