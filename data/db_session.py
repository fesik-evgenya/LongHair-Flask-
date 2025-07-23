import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

# Создаем декларативную базу
SqlAlchemyBase = declarative_base()

__factory = None


def global_init(db_file: str):
    """Инициализация глобального подключения к базе данных"""
    global __factory

    if __factory:
        return

    if not db_file or not db_file.strip():
        raise ValueError("Необходимо указать файл базы данных.")

    conn_str = f'sqlite:///{db_file.strip()}?check_same_thread=False'
    print(f"Подключение к базе данных по адресу {conn_str}")

    # Создаем движок
    engine = sa.create_engine(conn_str, echo=False)
    __factory = orm.sessionmaker(bind=engine)

    # Импортируем ВСЕ модели здесь, чтобы они зарегистрировались
    from . import customers, orders, products, loyalty  # noqa: F401

    # Создаем таблицы
    SqlAlchemyBase.metadata.create_all(engine)


def create_session() -> Session:
    """Создает новую сессию работы с базой данных"""
    global __factory
    if not __factory:
        raise RuntimeError("База данных не инициализирована. Вызовите global_init() сначала.")
    return __factory()