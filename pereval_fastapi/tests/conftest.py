# tests/conftest.py
import os
import sys
from pathlib import Path

# --- Гарантируем, что корень проекта в sys.path, чтобы 'app' импортировался корректно ---
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
import httpx
from httpx import ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Импорт Base (metadata) и, если есть, get_session из вашего приложения
try:
    from app.db import Base
except Exception as e:
    raise RuntimeError("Не удалось импортировать Base из app.db. Проверьте путь и наличие app/db.py") from e

try:
    from app.db import get_session as real_get_session
except Exception:
    real_get_session = None

# Тестовая БД: in-memory SQLite async
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "sqlite+aiosqlite:///:memory:")


@pytest.fixture(scope="session")
def anyio_backend():
    # Используем asyncio backend для anyio/pytest-asyncio
    return "asyncio"


@pytest.fixture(scope="session")
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)
    # Создаём таблицы (предварительно убедитесь, что все модели импортированы в app.db или при импорте Base)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    # Удаляем таблицы и закрываем engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture()
async def async_session(engine):
    """Создаёт отдельную асинхронную сессию для каждого теста и откатывает изменения после."""
    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
        try:
            await session.rollback()
        except Exception:
            pass


@pytest.fixture
async def async_client(async_session, monkeypatch):
    """
    Асинхронный httpx клиент, который вызывает FastAPI приложение через ASGITransport.
    Подменяет зависимость get_session на тестовую сессию, если такая зависимость используется.
    """
    # Импортируем app внутри фикстуры, чтобы избежать ранней инициализации при импорте conftest
    from app.main import app  # noqa: WPS433

    async def _get_test_session():
        yield async_session

    # Подмена зависимости: если в проекте используется Depends(get_session)
    if real_get_session is not None:
        app.dependency_overrides[real_get_session] = _get_test_session
    else:
        # Попытка подменить по модулю/имени (на случай, если get_session импортируется иначе)
        try:
            monkeypatch.setattr("app.db.get_session", _get_test_session, raising=False)
        except Exception:
            pass

    transport = ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
