from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

import os
import sys

# Добавляем путь к корневой директории проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Импортируем базовый класс моделей
from data.db_session import SqlAlchemyBase

# Это объект конфигурации Alembic
config = context.config

# Настраиваем логгирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем метаданные для автогенерации миграций
target_metadata = SqlAlchemyBase.metadata

def run_migrations_offline() -> None:
    """Запуск миграций в автономном режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,  # Важно для SQLite
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в онлайн режиме."""
    # Создаем движок из конфигурации
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Конфигурируем контекст миграции
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,  # Критически важно для работы с SQLite
            compare_type=True,      # Включаем сравнение типов
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()