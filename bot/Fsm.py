from file_manager import queries
from bot import config
import sqlite3 as sl


class FSM:

    def __init__(self):
        self.con = sl.connect(config.DATABASE_CONNECTION_STRING, check_same_thread=False)

    """ 
    Используется соединение с простой базой данных для малых проектов sqlite
    Данный класс содержит методы которые используют sql-запросы из файла file_manager.py/queries
    В свою очередь список queries получаем из файла sql_queries.json 
    В методах класса используются запросы проверки состояния, установления состояния.
    """

    def users_state_update(self, state, telegram_id) -> None:
        with self.con as con:
            con.execute(queries["state_update"], [state, telegram_id])

    def users_task_status_update(self, state, telegram_id) -> None:
        with self.con as con:
            con.execute(queries["task_status_update"], [state, telegram_id])

    def check_state(self, telegram_id) -> str:
        with self.con as con:
            return con.execute(queries["check_status"], [telegram_id]).fetchall()[0][0]

    def check_task_state(self, telegram_id) -> str:
        with self.con as con:
            return con.execute(queries["check_task_process"], [telegram_id]).fetchall()[0][0]

    def task_state_update(self, state, task_id) -> None:
        with self.con as con:
            con.execute(queries["task_change_state"], [state, task_id])


class DB:

    def __init__(self):
        self.con = sl.connect(config.DATABASE_CONNECTION_STRING, check_same_thread=False)

    """ 
        Используется соединение с простой базой данных для малых проектов sqlite
        Данный класс содержит методы которые используют sql-запросы из файла file_manager.py/queries
        В свою очередь список queries получаем из файла sql_queries.json
        В методах класса используются запросы по типу имя пользователя, id пользователя, id задачи и другие.
    """

    def searching_user(self, telegram_id) -> list:
        with self.con as con:
            return con.execute(queries["searching_user"], [telegram_id]).fetchall()

    def add_user(self, telegram_id, telegram_link) -> None:
        with self.con as con:
            con.execute(queries["adding_user"], [telegram_id, telegram_link])

    def write_name(self, name, telegram_id) -> None:
        with self.con as con:
            con.execute(queries["name_write"], [name, telegram_id])

    def login_write(self, login, telegram_id) -> None:
        with self.con as con:
            con.execute(queries["login_write"], [login, telegram_id])

    def get_id(self, telegram_id) -> int:
        with self.con as con:
            return con.execute(queries["user_id"], [telegram_id]).fetchall()[0][0]

    def get_name_login(self, telegram_id) -> tuple:
        with self.con as con:
            return con.execute(queries["users_name_login"], [telegram_id]).fetchall()[0]

    def get_name(self, telegram_id) -> str:
        with self.con as con:
            return con.execute(queries["users_name"], [telegram_id]).fetchall()[0][0]

    def get_login(self, telegram_id) -> str:
        with self.con as con:
            return con.execute(queries["users_login"], [telegram_id]).fetchall()[0][0]

    def find_tasks(self, telegram_id) -> list:
        with self.con as con:
            return con.execute(queries["searching_for_tasks"], [telegram_id]).fetchall()

    def get_task_name(self, task_id) -> str:
        with self.con as con:
            return con.execute(queries["task_name"], [task_id]).fetchall()[0][0]

    def get_task_name_state(self, task_id) -> tuple:
        with self.con as con:
            return con.execute(queries["task_name_and_state"], [task_id]).fetchall()[0]

    def get_tasks_id_name_on_state(self, state, telegram_id) -> list:
        with self.con as con:
            return con.execute(queries["searching_tasks_id_name_with_state"], [state, telegram_id]).fetchall()

    def get_task_info(self, task_id) -> tuple:
        with self.con as con:
            return con.execute(queries["task_description"], [task_id]).fetchall()[0]

    def create_task(self, user_id, task_name, task_description) -> None:
        with self.con as con:
            con.execute(queries["create_task"], [user_id, task_name, task_description])

    def delete_task(self, task_id) -> None:
        with self.con as con:
            con.execute(queries["delete_task"], [task_id])
