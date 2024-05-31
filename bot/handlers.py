from file_manager import texts_dict, buffer
from pyrogram import Client, types
import Keyboards
import Fsm

"""
    Импортирование из файла file_manager данных с текстовым словарём и буфером для редактирования или удаления
    сообщений, из pyrogram библиотеки клиент и типы, импорт файла Keyboards и Fsm,
    Содержит обработчики MessageHandlers, CallbackQueryHandler и функцию task_view 
"""


async def task_view(bot: Client, telegram_id, column, task_state):
    """
        В функцию передается клиент, id пользователя телеграмм, номер столбца слайда и состояние задачи,
        выполняется запрос к бд для получения списка задач с определённым(выполнена, не выполнена) состоянием
        задачи, получение количества групп по 5 задач, определение количества задач в последней группе,
        логика слайдов и выбор задач в слайд, создание клавиатуры и отправки сообщения с записью его id в буфер
    """
    tasks = bot_db.get_tasks_id_name_on_state(task_state, telegram_id)
    groups = (len(tasks) + 4) // 5
    last_group = len(tasks) - (len(tasks) % 5)
    slide = None
    tasks_list = None

    if column == 0 and groups == 1:
        slide = "no_pages"
        tasks_list = tasks[:5]

    elif column == 0 and groups > 1:
        slide = "first_page"
        tasks_list = tasks[:5]

    elif column == groups - 1 and groups > 1:
        slide = "last_page"
        tasks_list = tasks[last_group:]

    elif groups != column:
        slide = "last_page"
        tasks_list = tasks[column * 5:(column + 1) * 5]

    keyboard = bot_keyboards.task_viewer(tasks_list, slide, task_state)
    message_for_edit = await bot.edit_message_text(telegram_id, buffer["messages_for_edit"][telegram_id],
                                                   "📝Список ваших задач📝 : ", reply_markup=keyboard)
    buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})


async def start(bot: Client, message: types.Message):
    """
        Обработчик команды /start в боте, получение информации о пользователе из словаря сообщения,
        выполняется запрос к базе данных о записи пользователя в бд, реализованна логика если пользователь еще не
        сохранён в бд и наоборот.
    """
    telegram_id, telegram_link = message.from_user.id, "@" + message.from_user.username
    user_exists = bot_db.searching_user(telegram_id)

    if not user_exists:
        bot_db.add_user(telegram_id, telegram_link)
        registration_keyboard = bot_keyboards.welcome_keyboard()
        await bot.send_message(message.chat.id, ''.join(texts_dict['/start']),
                               reply_markup=registration_keyboard)

    else:
        user_login = bot_db.get_login(telegram_id)
        main_menu_keyboard = bot_keyboards.main_menu()
        greetings_text = (f"{texts_dict['for_registered'][0]} <b><i>{user_login}</i></b>"
                          f"\n{texts_dict['for_registered'][1]}")
        await bot.send_message(message.chat.id, greetings_text, reply_markup=main_menu_keyboard)


async def registration(bot: Client, message: types.Message):
    """
        Обработчик текстового сообщения: "Регистрация", отправка сообщения с краткой инструкцией,
        сам процесс регистрации довольно базовый, для тестового проекта.
    """
    telegram_id = message.from_user.id
    if message.text == "Регистрация":
        registration_keyboard = bot_keyboards.registration("Name")
        message_for_edit = await bot.send_message(message.chat.id, ''.join(texts_dict['Registration']),
                                                  reply_markup=registration_keyboard)
        buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})
    if message.text == "Помощь$":
        print("")  # TO DO


async def create_task(bot: Client, message: types.Message):
    """
    Обработчик текстового сообщения: "Создать задачу", в обработчике выполняются запросы к бд,
    такие-как существуют ли записи в бд о пользователе, проверки состояния его регистрации,
    удаление предыдущего сообщения отправленного ботом, отправки сообщения с inline клавиатурой,
    с записью id сообщения в словарь буффер
    """

    telegram_id = message.from_user.id
    user_exists = bot_db.searching_user(telegram_id)
    check_state = bot_fsm.check_state(telegram_id) if user_exists else None

    if telegram_id in buffer["messages_for_edit"].keys():
        await bot.delete_messages(telegram_id, buffer["messages_for_edit"][telegram_id])

    if check_state == "Зарегистрирован":
        keyboard = bot_keyboards.create_task("Новая задача")

        message_for_edit = await bot.send_message(message.chat.id,
                                                  ''.join(texts_dict["Task_create"]),
                                                  reply_markup=keyboard)

        buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})


async def task_overview(bot: Client, message: types.Message):
    """
        Обработчик текстового сообщения: "Просмотр задач", получение id пользователя из словаря сообщения,
        выполнение запроса к бд: поиск данных о пользователе, проверка его состояния регистрации, существования
        задач у пользователя, удалением предыдущего сообщения от бота, реализована логика отправки сообщения
        ботом если у пользователя есть записанные задачи в бд.
    """
    telegram_id = message.from_user.id
    user_exists = bot_db.searching_user(telegram_id)
    check_state = bot_fsm.check_state(telegram_id) if user_exists else None

    if telegram_id in buffer["messages_for_edit"].keys():
        await bot.delete_messages(telegram_id, buffer["messages_for_edit"][telegram_id])

    if check_state == "Зарегистрирован" and message.text == "Просмотр задач":
        tasks_in_db = bot_db.find_tasks(telegram_id)
        keyboard = bot_keyboards.task_state()

        if tasks_in_db:
            message_for_edit = await bot.send_message(message.chat.id,
                                                      texts_dict["Task_view"][1], reply_markup=keyboard)
            buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})
        else:
            await bot.send_message(message.chat.id, texts_dict["Task_view"][0])


async def profile(bot: Client, message: types.Message):
    """
        Обработчик сообщения: "Мой профиль", получение id пользователя из message,
        запросы к бд user_exists, check_state как и в предыдущих обработчиках,
        удаление предыдущего сообщения от бота пользователю,
        отправки сообщения с клавиатурой необходимых для внесения изменений в профиле,
        логика реализована очень базовая, для тестового проекта
    """

    telegram_id = message.from_user.id
    user_exists = bot_db.searching_user(telegram_id)
    check_state = bot_fsm.check_state(telegram_id) if user_exists else None

    if telegram_id in buffer["messages_for_edit"].keys():
        await bot.delete_messages(telegram_id, buffer["messages_for_edit"][telegram_id])

    if check_state == "Зарегистрирован":
        info = bot_db.get_name_login(telegram_id)
        name, login = info[0], info[1]

        profile_text = (f"{texts_dict['Profile'][0]}\n\nВаше имя: <b><i>{name}</i></b>\n\n"
                        f"Ваш логин: <b><i>{login}</i></b>\n\n{texts_dict['Profile'][0]}")

        keyboard = bot_keyboards.profile()

        message_for_edit = await bot.send_message(telegram_id, profile_text, reply_markup=keyboard)

        buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})


async def text(bot: Client, message: types.Message):
    """
    Обработчик всех текстовых сообщений которые не включают в себя сообщения в предыдущих обработчиках,
    как и прошлых обработчиках реализован сбор информации о пользователе из message и бд, так-же запрос
    о состоянии создания задачи пользователем к бд.
    """

    telegram_id = message.from_user.id
    user_exists = bot_db.searching_user(telegram_id)
    check_state = bot_fsm.check_state(telegram_id) if user_exists else None
    check_task_process = bot_fsm.check_task_state(telegram_id) if check_state else None

    if check_state == "Регистрация":
        registration_keyboard = bot_keyboards.registration("Name")

        await bot.delete_messages(message.chat.id, buffer["messages_for_edit"][telegram_id])

        message_for_edit = await bot.send_message(message.chat.id, ''.join(texts_dict['Registration']),
                                                  reply_markup=registration_keyboard)

        buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

    if check_state == "Ввод имени":

        login_button = bot_keyboards.registration("Login")
        user_name = bot_db.get_name(telegram_id)

        if user_name is None:
            bot_db.write_name(message.text, telegram_id)
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
        bot_db.login_write(message.text, telegram_id)
        bot_fsm.users_state_update("Зарегистрирован", telegram_id)
        user_name = bot_db.get_name(telegram_id)
        menu_keyboard = bot_keyboards.main_menu()
        await bot.send_message(message.chat.id,
                               texts_dict["Welcome"][0] + " " + user_name + "!\n" + ''.join(
                                   texts_dict["Welcome"][1:]),
                               reply_markup=menu_keyboard)

    if check_state == "Ввод нового имени":
        login = bot_db.get_login(telegram_id)
        bot_db.write_name(message.text, telegram_id)
        profile_text = (f"{texts_dict['Profile'][0]}\n\nВаше имя: <b><i>{message.text}</i></b>\n\n"
                        f"Ваш логин: <b><i>{login}</i></b>\n\n{texts_dict['Profile'][0]}")
        keyboard = bot_keyboards.profile()
        message_for_edit = await bot.send_message(telegram_id, profile_text, reply_markup=keyboard)
        bot_fsm.users_state_update("Зарегистрирован", telegram_id)
        buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

    if check_state == "Ввод нового логина":
        bot_db.login_write(message.text, telegram_id)
        name = bot_db.get_name(telegram_id)
        profile_text = (f"{texts_dict['Profile'][0]}\n\nВаше имя: <b><i>{name}</i></b>\n\n"
                        f"Ваш логин: <b><i>{message.text}</i></b>\n\n{texts_dict['Profile'][0]}")
        keyboard = bot_keyboards.profile()
        message_for_edit = await bot.send_message(telegram_id, profile_text, reply_markup=keyboard)
        bot_fsm.users_state_update("Зарегистрирован", telegram_id)
        buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

    if check_task_process == "Ввод имени":
        user_id = bot_db.get_id(telegram_id)
        keyboard = bot_keyboards.create_task("Описание задачи")
        message_for_edit = await bot.send_message(message.chat.id,
                                                  texts_dict["Task_name"][0] + message.text +
                                                  ''.join(texts_dict["Task_name"][1:]),
                                                  reply_markup=keyboard)
        buffer["creating_task"].update({telegram_id: [user_id, message.text]})
        buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})

    if check_task_process == "Ввод описания":
        bot_fsm.users_task_status_update("Не создаёт", telegram_id)
        task_name = buffer["creating_task"][telegram_id][1]
        task_description = message.text
        keyboard = bot_keyboards.create_task("Подтверждение создания")
        buffer["creating_task"][telegram_id].append(message.text)
        message_for_edit = await bot.send_message(message.chat.id,
                                                  texts_dict["Check_Task"][0] + task_name + "\n" + task_description
                                                  + "\n" + texts_dict["Check_Task"][1],
                                                  reply_markup=keyboard)
        buffer["messages_for_edit"].update({telegram_id: message_for_edit.id})


async def callback_query(bot: Client, call: types.CallbackQuery):
    """
    Обработчик callback_data в InlineKeyboardMarkup, реализована простая логика путём сверки данных об имени inline
    кнопок, множеством условных операторов if, для каждой кнопки реализована своя логика.
    """

    chat_id = call.message.chat.id
    button_name = call.data

    if button_name == "Name":
        bot_fsm.users_state_update("Ввод имени", chat_id)
        message_for_edit = await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                                       "Введите Имя:", reply_markup=None)
        buffer["messages_for_edit"].update({chat_id: message_for_edit.id})

    if button_name == "Login":
        bot_fsm.users_state_update("Ввод Логина", chat_id)
        message_for_edit = await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                                       "Введите Логин:", reply_markup=None)
        buffer["messages_for_edit"].update({chat_id: message_for_edit.id})

    if button_name == "change_name":
        bot_fsm.users_state_update("Ввод нового имени", chat_id)
        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id], "Введите новое имя: ",
                                    reply_markup=None)

    if button_name == "change_login":
        bot_fsm.users_state_update("Ввод нового логина", chat_id)
        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id], "Введите новый логин: ",
                                    reply_markup=None)

    if button_name == "cancel_profile":
        await bot.delete_messages(chat_id, buffer["messages_for_edit"][chat_id])

    if button_name == "task_name":
        bot_fsm.users_task_status_update("Ввод имени", chat_id)
        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                    "Введите название задачи: ")

    if button_name == "task_description":
        bot_fsm.users_task_status_update("Ввод описания", chat_id)
        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                    "Введите описание задачи: ")

    if button_name == "task_accept":
        user_id = buffer["creating_task"][chat_id][0]
        task_name = buffer["creating_task"][chat_id][1]
        task_description = buffer["creating_task"][chat_id][2]
        bot_db.create_task(user_id, task_name, task_description)
        buffer["creating_task"].pop(chat_id)
        await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                    f"Ваша зада {task_name} успешно создана.\n"
                                    f"Посмотреть задачу вы можете в навигационном меню 'Просмотр задач'")

    if button_name == "Cancel_task_creating":

        bot_fsm.users_task_status_update("Не создаёт", chat_id)
        if chat_id in buffer["creating_task"].keys():
            buffer["creating_task"].pop(chat_id)
        await bot.delete_messages(chat_id, buffer["messages_for_edit"][chat_id])

    if button_name == "active_tasks":

        tasks = bot_db.get_tasks_id_name_on_state("Не выполнена", chat_id)
        print(tasks)

        if tasks:
            buffer["task_groups"].update({chat_id: {"active_slide": 0, "task_state": "Не выполнена"}})
            await task_view(bot, chat_id, column=0, task_state="Не выполнена")

        else:
            state_text = f"{texts_dict['tasks_left'][0]} активных {texts_dict['tasks_left'][1]}"
            keyboard = bot_keyboards.task_menu()
            await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                        state_text, reply_markup=keyboard)

    if button_name == "not_active_tasks":

        tasks = bot_db.get_tasks_id_name_on_state("Выполнена", chat_id)

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
        task_info = bot_db.get_task_info(task_id)
        task_name, task_description = task_info[0], task_info[1]
        active_text, inactive_state = texts_dict['task_info'][0], texts_dict['task_info'][1]
        task_state = active_text if buffer["task_groups"][chat_id]["task_state"] == "Не выполнена" else inactive_state
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
        status_text = "активных" if task_state == "Не выполнена" else "не активных"
        task_name = bot_db.get_task_name(task_id)
        bot_db.delete_task(task_id)
        task_left = bot_db.get_tasks_id_name_on_state(task_state, chat_id)
        await bot.answer_callback_query(call.id, f"Задача {task_name} удалена")

        if task_left:
            await task_view(bot, chat_id, column=0, task_state=task_state)

        else:
            state_text = f"{texts_dict['tasks_left'][0]} {status_text} {texts_dict['tasks_left'][1]}"
            keyboard = bot_keyboards.task_menu()
            await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                        state_text, reply_markup=keyboard)

    if button_name.startswith("change_state"):

        task_id = button_name[13:]
        name_and_state = bot_db.get_task_name_state(task_id)
        task_name, task_state = name_and_state[0], name_and_state[1]
        status_text = "активных" if task_state == "Не выполнена" else "не активных"

        if task_state == "Не выполнена":
            new_state = f"Задача {task_name} не активна"
            bot_fsm.task_state_update("Выполнена", task_id)
        else:
            new_state = f"Задача {task_name} активна"
            bot_fsm.task_state_update("Не выполнена", task_id)

        task_left = bot_db.get_tasks_id_name_on_state(task_state, chat_id)
        await bot.answer_callback_query(call.id, new_state)

        if task_left:
            await task_view(bot, chat_id, column=0, task_state=task_state)
        else:
            state_text = f"{texts_dict['tasks_left'][0]} {status_text} {texts_dict['tasks_left'][1]}"
            keyboard = bot_keyboards.task_menu()
            await bot.edit_message_text(chat_id, buffer["messages_for_edit"][chat_id],
                                        state_text, reply_markup=keyboard)


"""
    Создание 3 экземпляров, такие как:
    - из файла Keyboards класс BotKeyboards, который содержит необходимые клавиатуры,
    - 2 экземпляра классов с запросами к бд.
"""
bot_keyboards = Keyboards.BotKeyboards()
bot_fsm = Fsm.FSM()
bot_db = Fsm.DB()
