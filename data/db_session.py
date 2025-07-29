import sqlalchemy as sa
import sqlalchemy.orm as orm
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base

# Создаем декларативную базу
SqlAlchemyBase = declarative_base()

__factory = None
engine = None  # Глобальный объект движка


def global_init(db_conn_str: str):
    """Инициализация глобального подключения к базе данных"""
    global __factory, engine

    if __factory:
        return

    if not db_conn_str or not db_conn_str.strip():
        raise ValueError("Необходимо указать строку подключения к базе данных.")

    print(f"Подключение к базе данных по адресу: {db_conn_str}")

    try:
        # Создаем движок с настройками для PostgreSQL
        engine = sa.create_engine(
            db_conn_str,
            echo=False,  # Отключаем вывод SQL в консоль (False для продакшена)
            pool_pre_ping=True,  # Автоматическая проверка соединения перед использованием
            pool_size=10,  # Размер пула соединений
            max_overflow=20,  # Максимальное количество соединений сверх pool_size
            pool_recycle=3600  # Пересоздавать соединения каждый час
        )

        __factory = orm.sessionmaker(bind=engine)

        # Импортируем ВСЕ модели здесь, чтобы они зарегистрировались
        from . import customers, orders, products, loyalty, employees  # noqa: F401

        # Создаем таблицы (если они еще не существуют)
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

    # Создаем и возвращаем сессию
    session = __factory()

    # Для PostgreSQL рекомендуется явно устанавливать уровень изоляции
    session.connection(execution_options={
        "isolation_level": "READ COMMITTED"
    })

    return session


# Функция для закрытия всех соединений
def shutdown_session():
    global engine
    if engine:
        engine.dispose()
        print("Соединения с базой данных закрыты")