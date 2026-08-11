# app/db.py
import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL для async SQLAlchemy
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    fstr_login = os.getenv("FSTR_DB_LOGIN") or os.getenv("FSTR_LOGIN")
    fstr_pass = os.getenv("FSTR_DB_PASS") or os.getenv("FSTR_PASS")
    fstr_host = os.getenv("FSTR_DB_HOST", "localhost")
    fstr_port = os.getenv("FSTR_DB_PORT", "5432")
    fstr_name = os.getenv("FSTR_DB_NAME") or os.getenv("FSTR_DB")
    if fstr_login and fstr_pass and fstr_name:
        DATABASE_URL = (
            f"postgresql+asyncpg://{fstr_login}:{fstr_pass}@{fstr_host}:{fstr_port}/{fstr_name}"
        )
    else:
        DATABASE_URL = "sqlite+aiosqlite:///./pereval.db"

# ASYNC engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# ASYNC session maker
async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# ВАЖНО: Base должен существовать, иначе тесты падают
Base = declarative_base()

# Импортируем модели здесь, чтобы Base.metadata знало о них при create_all.
# Это важно для тестовой среды, где промежуточный модуль app.db запускает создание схемы до импорта app.main.
from app.models.user import User  # noqa: F401, E402
from app.models.coords import Coords  # noqa: F401, E402
from app.models.level import Level  # noqa: F401, E402
from app.models.image import Image  # noqa: F401, E402
from app.models.pereval import Pereval  # noqa: F401, E402


# ВАЖНО: именно эту функцию импортируют роутеры и подменяют тесты
async def get_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
