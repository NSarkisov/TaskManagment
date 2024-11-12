import json

"""
    В данном модуле реализованна логика чтения файлов, таких как config.json, sql_queries.json, texts.json,
    с записью переменных для последующего импорта в других файлов приложения, переменная словаря буфер 
"""

with open("/TaskManagment/db/sql_queries.json") as file:
    config = json.load(file)
    queries = config.get("queries")


with open("/TaskManagment/db/texts.json", "r", encoding='utf-8') as file:
    config = json.load(file)
    texts_dict = config.get("texts")


buffer = {
    "messages_for_edit": {},
    "creating_task": {},
    "task_groups": {}

}  # telegram_id: message.id



