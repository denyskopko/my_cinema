from fastapi import FastAPI, Request, Depends, Query
from app.database import get_db
from fastapi.staticfiles import StaticFiles
from app.crud import get_filter_metadata, search_films_by_title, search_films_by_filters
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates
from app.models import Film
from typing import Optional
from app.mongodb import save_search_query, get_popular_queries, get_recent_queries

app = FastAPI()

# Подключение папки сCSS
app.mount("/static", StaticFiles(directory="static"), name="static")
# Инициализация  Jinja2
templates = Jinja2Templates(directory="templates")


@app.get("/")
def home(request: Request, db: Session = Depends(get_db), page: int = 0):
    """
    Главная страница: отображает список всех фильмов из БД
    пагинация по (по 10 штук).
    """
    # Запрос получаем 10 фильмов с (offset)
    films = db.query(Film).limit(10).offset(page * 10).all()
    # Получаем данные для фильтров (список жанров и границы годов)
    meta = get_filter_metadata(db)
    # Получаем ТОП-5 популярных запросов из MongoDB и последних
    popular = get_popular_queries(5)
    recent = get_recent_queries(5)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "films": films,
        "meta": meta,
        "page": page,
        "popular_queries": popular,
        "recent_queries": recent

    })


@app.get("/search")
def search(request: Request, q: str = Query(None), page: int = 0, db: Session = Depends(get_db)):
    """Поиск фильма по названию. Сохраняет запрос в MongoDB и ищет совпадения в MySQL."""
    meta = get_filter_metadata(db)
    if q:
        # Сохранение текста запроса в базу MongoDB
        if page == 0:
            save_search_query(q)
        # Вызов функции поиска 
        films = search_films_by_title(db, q, page)
    else:
        films = []
    popular = get_popular_queries(5)
    recent = get_recent_queries(5)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "films": films,
        "meta": meta,
        "query": q,
        "page": page,
        "popular_queries": popular,
        "recent_queries": recent
    })


@app.get("/filter")
def filter_search(
        request: Request,
        cat_id: Optional[str] = Query(None),
        y_from: Optional[str] = Query(None),
        y_to: Optional[str] = Query(None),
        page: int = Query(0),
        db: Session = Depends(get_db)
):
    """фильтр: поиск по выбранному жанру и или диапазону годов выпуска."""
    meta = get_filter_metadata(db)

    #  функция для безопасного перевода строк в числа
    def safe_int(val):
        if val is None or str(val).strip() == "":
            return None
        try:
            return int(val)
        except ValueError:
            return None

    clean_cat_id = safe_int(cat_id)
    clean_y_from = safe_int(y_from)
    clean_y_to = safe_int(y_to)

    # Запрос к БД с применением всех фильтров
    films = search_films_by_filters(db, clean_cat_id, clean_y_from, clean_y_to, page)
    popular = get_popular_queries(5)
    recent = get_recent_queries(5)

    return templates.TemplateResponse("index.html", {
        "request": request, "films": films, "meta": meta, "page": page,
        "selected_cat": clean_cat_id, "year_from": clean_y_from, "year_to": clean_y_to,
        "popular_queries": popular,
        "recent_queries": recent
    })


@app.get("/genre/{cat_id}")
def get_genre_page(request: Request, cat_id: int, page: int = Query(0), db: Session = Depends(get_db)):
    """Отдельная страница для конкретного жанра."""
    meta = get_filter_metadata(db)
    # Ищем фильмы, связанные с конкретным category_id
    films = search_films_by_filters(db, category_id=cat_id, page=page)

    # Находим название текущего жанра в списке метаданных
    current_genre_name = next((c.name for c in meta["genres"] if c.category_id == cat_id), "Неизвестный жанр")
    popular = get_popular_queries(5)
    recent = get_recent_queries(5)
    return templates.TemplateResponse("genre.html", {
        "request": request, "films": films, "meta": meta, "cat_id": cat_id,
        "current_genre": current_genre_name, "selected_cat": cat_id, "page": page,
        "popular_queries": popular,
        "recent_queries": recent
    })


if __name__ == "__main__":
    import uvicorn

    # Запуск сервера в локе , порт 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)
