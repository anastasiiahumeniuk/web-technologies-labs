import os
import sys

sys.path.append(os.getcwd())

from app.database.sessions import engine, BaseModel

def init_db():
    print(f"Підключаюсь до бази даних: {engine.url}")
    print("Cтворюю таблиці...")

    try:
        BaseModel.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"Помилка при створенні БД: {e}")
        sys.exit(1)

    print("Таблиці створені.")


if __name__ == "__main__":
    init_db()
