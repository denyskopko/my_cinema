from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")  # url для подключения к бд
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    print("Проверка подключения к базе данных...")
    try:
        # Пробуем выполнить простейший запрос
        db_gen = get_db()
        db = next(db_gen)
        db.execute(text("SELECT 1"))
        print("Подключение успешно установлено!")
    except Exception as e:
        print(f"Ошибка подключения: {e}")
