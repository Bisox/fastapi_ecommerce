import sys
from os.path import abspath, dirname

from logging.config import fileConfig

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy import pool

from alembic import context

from app.models import *

from config import settings  # Импортируйте настройки
from app.backend.db import Base  # Импортируйте вашу базу данных

# Добавьте свой путь к проекту
sys.path.insert(0, dirname(dirname(dirname(abspath(__file__)))))


# Получение конфигурации Alembic
config = context.config

# Установка строки подключения из настроек
config.set_main_option('sqlalchemy.url', settings.DATABASE_URL)

# Интерпретация файла конфигурации для Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Добавьте MetaData вашего модуля здесь
target_metadata = Base.metadata


# Двигатель конфигурации для offline режима
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"}
    )

    with context.begin_transaction():
        context.run_migrations()


# Двигатель конфигурации для online режима
async def run_migrations_online():  # new
    """Run migrations in 'online' mode."""

    # Создаем асинхронный движок
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


# Функция для выполнения миграций в синхронном контексте
def do_run_migrations(connection):  # new
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


# Запуск миграций в зависимости от режима
if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())
