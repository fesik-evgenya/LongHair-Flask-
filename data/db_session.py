import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

# Создаем декларативную базу
SqlAlchemyBase = declarative_base()

__factory = None
engine = None  # Глобальный объект движка


def global_init(db_conn_str: str):  # Параметр правильно называется db_conn_str
    """Инициализация глобального подключения к базе данных"""
    global __factory, engine

    if __factory:
        return

    if not db_conn_str or not db_conn_str.strip():
        raise ValueError("Необходимо указать строку подключения к базе данных.")

    print(f"Подключение к базе данных по адресу: {db_conn_str}")

    try:
        # Автоматическое определение типа БД по строке подключения
        if db_conn_str.startswith("postgresql://"):  # Исправлено: db_conn_str
            # Настройки для PostgreSQL
            engine = sa.create_engine(
                db_conn_str,  # Исправлено: db_conn_str
                echo=False,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                pool_recycle=3600
            )
        elif db_conn_str.startswith("sqlite://"):  # Исправлено: db_conn_str
            # Настройки для SQLite (для локальной разработки)
            engine = sa.create_engine(
                db_conn_str,  # Исправлено: db_conn_str
                echo=False,
                connect_args={"check_same_thread": False}
            )
        else:
            raise ValueError(f"Неподдерживаемый тип базы данных в строке подключения: {db_conn_str}")  # Исправлено

        __factory = orm.sessionmaker(bind=engine)

        # Импортируем модели
        from . import customers, orders, products, loyalty, employees

        # Создаем таблицы
        SqlAlchemyBase.metadata.create_all(engine)
        print("Таблицы успешно созданы/проверены")

    except Exception as e:
        print(f"Ошибка при подключении к базе данных: {str(e)}")
        raise


def create_session() -> Session:
    """Создает новую сессию работы с базой данных"""
    global __factory
    if not __factory:
        raise RuntimeError("База данных не инициализирована. Вызовите global_init() сначала.")

    return __factory()


def shutdown_session():
    """Закрывает все соединения с базой данных"""
    global engine
    if engine:
        engine.dispose()
        print("Соединения с базой данных закрыты")