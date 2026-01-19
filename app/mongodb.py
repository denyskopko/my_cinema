from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

MONGODB_URL_EDIT = os.getenv("MONGODB_URL_EDIT")

client_read = MongoClient(MONGODB_URL_EDIT)
client_edit = MongoClient(MONGODB_URL_EDIT)

db_read = client_read["ich_edit"]
db_edit = client_edit["ich_edit"]

COLLECTION_NAME = "final_project_010825-ptm_denys_kopko"


def save_search_query(query: str):
    """Сохранение запроса."""
    if not query or not query.strip():
        return
    clean_query = query.lstrip().rstrip().lower()
    try:
        db_edit[COLLECTION_NAME].update_one(
            {"query": clean_query},
            {
                "$set": {"last_searched": datetime.now()},
                "$inc": {"count": 1}
            },
            upsert=True
        )
    except Exception as e:
        print(f"Ошибка записи в MongoDB: {e}")

def get_popular_queries(limit: int = 5):
    """Самые популярные (query + count)"""
    try:
        # Получаем и текст, и количество
        cursor = db_read[COLLECTION_NAME].find().sort("count", -1).limit(limit)
        return [{"query": doc["query"], "count": doc.get("count", 0)} for doc in cursor]
    except Exception as e:
        print(f"Ошибка чтения популярных (get_popular_queries): {e}")
        return []

def get_recent_queries(limit: int = 5):
    """Недавние (query + count)"""
    try:
        cursor = db_read[COLLECTION_NAME].find().sort("last_searched", -1).limit(limit)
        return [{"query": doc["query"], "count": doc.get("count", 0)} for doc in cursor]
    except Exception as e:
        print(f"Ошибка чтения последних (get_recent_queries): {e}")
        return []


if __name__ == "__main__":
    print("--- Проверка подключения к MongoDB ---")
    try:
        # 1. Тестовая запись
        test_q = "small_test"
        save_search_query(test_q)
        print(f"Запрос '{test_q}' успешно обработан в коллекции: {COLLECTION_NAME}")

        # 2. Получение данных
        popular = get_popular_queries(5)
        recent = get_recent_queries(5)

        print("\n ТОП Популярных:")
        for item in popular:
            print(f" - {item['query']}: {item['count']} раз(а)")

        print("\n ТОП Недавних:")
        for item in recent:
            print(f" - {item['query']} (всего поисков: {item['count']})")

        print("\n--- тестирование завершено успешно ---")
    except Exception as e:
        print(f" ошибка при тестировании: {e}")

