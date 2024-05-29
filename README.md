# TaskManagment

[![Python Version](https://img.shields.io/badge/Python-3.11-blue.svg?logo=python)](https://www.python.org/downloads/release/python-3210/)

Telegram-бот для управления задачами пользователей.

## Переменные окружения

- `TELEGRAM_BOT_TOKEN`: API ключ от Telegram-бота. Его можно получить у [Отца ботов](https://telegram.me/botfather). Введите команду `/newbot` в чате с ним и следуйте инструкциям.
- `API_ID`: идентификатор API, полученный от [платформы API Telegram](https://my.telegram.org/apps).
- `API_HASH`: хеш API, полученный от [платформы API Telegram](https://my.telegram.org/apps).
- `DATABASE_CONNECTION_STRING`: Ссылка с параметрами БД в формате - `../каталог/базаданных.db` . Например, `../db/sqlite_db.db` .

## Запуск приложения через консоль

- Клонируем ссылку

  ```bash
  git clone https://github.com/NSarkisov/TaskManagment
  ```
- Переходим в папку с локальным проектом

  ```bash
  cd TaskManagment
  ```
- Устанавливаем виртуальное окружение.
  
  Python 3.11 уже должен быть установлен на компьютер.

  Создаём виртуальное окружение Linux/Mac:
  ```bash
  python3 -m venv venv
  ```
  Создаём виртуальное окружение Windows:
    ```bash
  python -m venv venv
  ```

  Если у Вас на компьютере несколько версий python используйте эту команду для создания виртуального окружения:
  ```bash
  py -3.11 -m venv venv
  ```
  Активируем окружение, выполнив команду в терминале:
  ```bash
  source venv/bin/activate
  ```
  В Windows для запуска виртуального окружения выполните команду в командной строке:
  ```shell
  venv\Scripts\activate
  ```
- Перейдите в рабочий каталог:
  ```bash
  cd Task_Managment
  ```
- Для виртуального окружения принимаем зависимости:
  ```bash
  pip install -r requirements.txt
  ```
- Создаём файл .env и прописываем переменные окружения.
- Обязательно прописываем все параметры, находящиеся в .env.example

- Запускаем локальный сервер:
  ```bash
  python main.py
  ```

## Запуск приложения через docker

- Клонируем ссылку

  ```bash
  git clone https://github.com/NSarkisov/TaskManagment
  ```

- Переходим в папку с локальным проектом

  ```bash
  cd TaskManagment
  ```

- Создаём новый файл .env (пример заполнения есть в .env.example) и подставляем значения.

  ```bash
  cp example.env .env
  ```
- Запускаем docker-compose файл

  ```bash
  docker-compose up --build
  ```

## Используемые технологии
- Python 3.11
- sqlite3
- Pyrogram

## Функционал

1. Telegram-бота на Python с использованием библиотеки Pyrogram.
2. Бот имеет следующие функциональности:
    1. Регистрация новых пользователей:
        1. При первом входе пользователю предоставлена возможность зарегистрироваться в системе, введя свое имя и выбрав уникальный логин.
        2. Информация о зарегистрированных пользователях сохранится в базе данных.
    2. Создание задач:
        1. Зарегистрированный пользователь имеет возможность создавать новые задачи, указывая их название и описание.
        2. Информация о задачах сохраняется в базе данных и связана с соответствующим пользователем.
    3. Просмотр и управление задачами:
        1. Пользователь имеет возможность просматривать список своих задач.
        2. Бот предоставляет интерфейс для управления задачами:
            - возможность пометить задачу как выполненную (изменить статус задачи);
            - возможность удалить задачу.
    4. Использование постоянных и inline меню:
        1. Бот должен использовать постоянные меню для навигации по функциональностям
        2. Бот должен использовать inline меню для взаимодействия с конкретными задачами.
    5. Выполнение SQL-запросов:
        1. Бот должен уметь выполнять SQL-запросы к базе данных.
        2. Результаты запросов должны быть корректно обработаны и представлены пользователю.

## Цель

Тестовое задание


