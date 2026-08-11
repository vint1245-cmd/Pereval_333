# app/repositories/submit_repository.py
from typing import List, Optional

from sqlalchemy.orm import Session, selectinload
from sqlalchemy import select

from app import models


class SubmitRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, pereval_id: int) -> Optional[models.Pereval]:
        """
        Возвращает Pereval по id с подгруженными связями.
        """
        stmt = (
            select(models.Pereval)
            .options(
                selectinload(models.Pereval.user),
                selectinload(models.Pereval.coords),
                selectinload(models.Pereval.level),
                selectinload(models.Pereval.images),
            )
            .where(models.Pereval.id == pereval_id)
        )
        return self.db.execute(stmt).scalars().first()

    def get_by_user_email(self, email: str) -> List[models.Pereval]:
        """
        Возвращает все Pereval, связанные с пользователем по email.
        """
        stmt = (
            select(models.Pereval)
            .join(models.User)
            .options(
                selectinload(models.Pereval.user),
                selectinload(models.Pereval.coords),
                selectinload(models.Pereval.level),
                selectinload(models.Pereval.images),
            )
            .where(models.User.email == email)
        )
        return self.db.execute(stmt).scalars().all()

    def create(self, pereval: models.Pereval) -> models.Pereval:
        """
        Создаёт Pereval.
        """
        self.db.add(pereval)
        self.db.commit()
        self.db.refresh(pereval)
        return pereval

    def update(self, pereval: models.Pereval) -> models.Pereval:
        """
        Обновляет Pereval.
        """
        self.db.add(pereval)
        self.db.commit()
        self.db.refresh(pereval)
        return pereval
