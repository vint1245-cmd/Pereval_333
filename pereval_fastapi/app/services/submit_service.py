# app/services/submit_service.py
from typing import List, Optional

from sqlalchemy.orm import Session

from app.repositories.submit_repository import SubmitRepository
from app import models
from app.schemas.pereval import PerevalOut


class SubmitService:
    def __init__(self, db: Session):
        self.repo = SubmitRepository(db)

    def get_pereval_by_id(self, pereval_id: int) -> Optional[PerevalOut]:
        obj = self.repo.get_by_id(pereval_id)
        if not obj:
            return None
        return PerevalOut.from_orm(obj)

    def get_perevals_by_user_email(self, email: str) -> List[PerevalOut]:
        objs = self.repo.get_by_user_email(email)
        return [PerevalOut.from_orm(o) for o in objs]
