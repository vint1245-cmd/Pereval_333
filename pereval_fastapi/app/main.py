from fastapi import FastAPI
from app.routers import submitdata
from app.db import engine, Base
import os



app = FastAPI(
    title="Pereval FSTR API",
    description="FastAPI-реализация проекта Pereval для стажировки SkillFactory",
    version="1.0.0",
)

app.include_router(submitdata.router, prefix="/api/v1")


@app.on_event("startup")
async def on_startup():
    # Для локальной разработки: по умолчанию создаём таблицы при старте.
    # Чтобы отключить автосоздание (например, в продакшне), установите
    # переменную окружения `SKIP_CREATE_TABLES=1`.
    skip = os.getenv("SKIP_CREATE_TABLES", "0")
    if skip == "1":
        return

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
