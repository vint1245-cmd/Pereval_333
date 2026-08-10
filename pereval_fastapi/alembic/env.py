import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# --- ВАЖНО: путь к app/ ---
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db import Base, DATABASE_URL  # импортируем Base и URL
from app.models.user import User
from app.models.coords import Coords
from app.models.level import Level
from app.models.pereval import Pereval
from app.models.image import Image

# Alembic Config
config = context.config

# Подключаем логирование
fileConfig(config.config_file_name)

# Указываем метаданные моделей
target_metadata = Base.metadata


def run_migrations_offline():
    """Запуск миграций без подключения к БД."""
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Запуск миграций с подключением к БД."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
