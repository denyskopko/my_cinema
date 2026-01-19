from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Category, Film, FilmCategory
from functools import lru_cache
from app.database  import get_db


def search_films_by_title(db: Session, title_query: str, page: int = 0):
    """Поиск фильмов по слову в названии."""
    try:
        return db.query(Film).filter(Film.title.ilike(f"%{title_query}%")).limit(10).offset(page * 10).all()
    except Exception as e:
        print(f"Ошибка поиска по названию (search_films_by_title): {e}")
        return []



@lru_cache(maxsize=1)  # на 2  запроса  меньше (SELECT * FROM category и SELECT MIN/MAX)
def get_filter_metadata(db: Session):
    # Запрос всех категорий жанров из таблицы Category
    try:
        """остальные данные для html"""
        genres = db.query(Category).all()
        # запрос для поиска минимального и максимального года в таблице Film
        years = db.query(func.min(Film.release_year), func.max(Film.release_year)).first()
        return {
            "genres": genres,
            "min_year": years[0] if years and years[0] is not None else None,
            "max_year": years[1] if years and years[1] is not None else None
        }
    except Exception as e:
        print(f"Ошибка получения метаданных (get_filter_metadata): {e}")
        return {"genres": [], "min_year": None, "max_year": None}



def search_films_by_filters(db: Session, category_id: int = None,
                            year_from: int = None, year_to: int = None, page: int = 0):
    """поиск по жанру и диапазону лет выпуска с None"""
    try:
        query = db.query(Film)
        # Если указан жанр -->JOIN
        if category_id:
            query = query.join(FilmCategory).filter(FilmCategory.category_id == category_id)
        # Если указана нижняя граница года
        if year_from is not None:
            query = query.filter(Film.release_year >= year_from)
        # Если указана верхняя граница года
        if year_to is not None:
            query = query.filter(Film.release_year <= year_to)
            # результат для вывода в html
        return query.limit(10).offset(page * 10).all()
    except Exception as e:
        print(f"Ошибка поиска по фильтрам (search_films_by_filters): {e}")
        return []


if __name__ == "__main__":
    print("Проверка подключения и работы функций...")
    try:
        db_gen = get_db()
        db_session = next(db_gen)

        print(f"Тестирование search_films_by_title...")
        films = search_films_by_title(db_session, "ACADEMY")

        print(f"Тестирование get_filter_metadata...")
        get_filter_metadata.cache_clear()
        metadata = get_filter_metadata(db_session)

        print(f"Тестирование search_films_by_filters...")
        p0 = search_films_by_filters(db_session, category_id=1, year_from=2000, page=0)
        p1 = search_films_by_filters(db_session, category_id=1, year_from=2000, page=1)

        print(f"Результаты поиска по названию (кол-во): {len(films)}")
        print(f"Результаты метаданных: {len(metadata['genres'])} жанров")
        print(f"Пагинация: стр 0 ({len(p0)} элемент), стр 1 ({len(p1)} элемент)")

        # Добавлена проверка на наличие элементов
        if len(p0) > 0 and len(p1) > 0 and p0[0].film_id != p1[0].film_id:
            print("Проверка пагинации: Успешно (ID на страницах разные)")
        elif len(p0) > 0 and len(p1) == 0:
            print("Проверка пагинации: Успешно (вторая страница пуста, данных мало)")

        print("Тестирование функций завершено успешно.")

    except Exception as e:
        print(f"Ошибка при тестировании модуля: {e}")