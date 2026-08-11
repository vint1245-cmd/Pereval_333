from fastapi import FastAPI
from app.routers import submitdata

app = FastAPI(
    title="Pereval FSTR API",
    description="FastAPI-реализация проекта Pereval для стажировки SkillFactory",
    version="1.0.0",
)

app.include_router(submitdata.router, prefix="/api/v1")
