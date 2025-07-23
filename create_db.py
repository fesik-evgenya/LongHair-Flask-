import os
from data.db_session import global_init


def create_database():
    # Создаем папку db, если её нет
    db_dir = 'db'
    os.makedirs(db_dir, exist_ok=True)

    # Путь к базе данных
    db_path = os.path.join(db_dir, 'shop.db')

    # Инициализируем базу данных
    global_init(db_path)
    print(f"База данных успешно создана: {db_path}")


if __name__ == '__main__':
    create_database()