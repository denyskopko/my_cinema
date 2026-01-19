from sqlalchemy import Column, SmallInteger, String, Text, Enum, DECIMAL, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.mysql import TINYINT, SET, YEAR
from app.database import Base


class Film(Base):
    """Класс для таблицы `film` """
    __tablename__ = "film"
    film_id = Column(SmallInteger, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    description = Column(Text)
    release_year = Column(YEAR)
    language_id = Column(TINYINT(unsigned=True), nullable=False)
    original_language_id = Column(TINYINT(unsigned=True))
    rental_duration = Column(TINYINT(unsigned=True), nullable=False, default=3)
    rental_rate = Column(DECIMAL(4, 2), nullable=False, default=4.99)
    length = Column(SmallInteger)
    replacement_cost = Column(DECIMAL(5, 2), nullable=False, default=19.99)
    rating = Column(Enum("G", "PG", "PG-13", "R", "NC-17"), default="G")
    special_features = Column(SET("Trailers", "Commentaries", "Deleted Scenes", "Behind the Scenes"))

    # Связь: позволяет доставать категории через film.categories
    categories = relationship("Category", secondary="film_category", back_populates="films")

    def __repr__(self) -> str:
        return f"Film(id={self.film_id}, title='{self.title}')"


class Category(Base):
    """Класс для таблицы `category` """
    __tablename__ = "category"
    category_id = Column(TINYINT(unsigned=True), primary_key=True, autoincrement=True)
    name = Column(String(25), nullable=False)

    # Связь: фильмы через category.films
    films = relationship("Film", secondary="film_category", back_populates="categories")

    def __repr__(self) -> str:
        return f"Category(id={self.category_id}, name='{self.name}')"


class FilmCategory(Base):
    """Таблица связи фильмов и категорий """
    __tablename__ = "film_category"

    film_id = Column(SmallInteger, ForeignKey("film.film_id"), primary_key=True)
    category_id = Column(TINYINT(unsigned=True), ForeignKey("category.category_id"), primary_key=True)


