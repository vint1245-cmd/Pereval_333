# app/services/submit_service.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLalchemyError

from app.repositories.submit_repository import SubmitRepository
from app import models
from app.schemas.pereval import PerevalOut
from app.schemas.user import UserCreate
from app.schemas.coords import CoordsCreate
from app.schemas.level import LevelCreate
from app.schemas.image import ImageCreate


class SubmitService:
    def __init__(self, db: Session):
        self.repo = SubmitRepository(db)
        self.db = db

    def get_pereval_by_id(self, pereval_id: int) -> Optional[PerevalOut]:
        obj = self.repo.get_by_id(pereval_id)
        if not obj:
            return None
        return PerevalOut.from_orm(obj)

    def get_perevals_by_user_email(self, email: str) -> List[PerevalOut]:
        objs = self.repo.get_by_user_email(email)
        return [PerevalOut.from_orm(o) for o in objs]
    
    def create_pereval(self, payload: PerevalCreate) -> models.Pereval:
        # Создает перевал с вложенными user, coords, level, images
        # если пользователь с таким email уже существует, то не создаем нового пользователя, а используем существующего
        try:
            user_data = payload.user
            user = (
                self.db.query(models.User)
                .filter(models.User.email == user_data.email)
                .first()
            )
            if not user:
                user = models.User(
                    email=user_data.email,
                    phone=user_data.phone,
                    fam=user_data.fam,
                    name=user_data.name,
                    otc=user_data.otc,
                )
                self.db.add(user)
                self.db.flush()

        # Coords
            coords_data = payload.coords
            coords = models.Coords(
                latitude=coords_data.latitude,
                longitude=coords_data.longitude,
                height=coords_data.height,
            )
            self.db.add(coords)
            self.db.flush()

        # Level
            level_data = payload.level
            level = models.Level(
                winter=level_data.winter,
                summer=level_data.summer,
                autumn=level_data.autumn,
                spring=level_data.spring,
            )
            self.db.add(level)
            self.db.flush()

        # Pereval
            pereval = models.Pereval(
                beauty_title=payload.beauty_title,
                title=payload.title,
                other_titles=payload.other_titles,
                connect=payload.connect,
                status="new",
                user_id=user.id,
                coords_id=coords.id,
                level_id=level.id,
            )
            self.db.add(pereval)
            self.db.flush()

        # Images
            for img in payload.images:
                image = models.Image(pereval_id=pereval.id, data=img.data, title=img.title)
                self.db.add(image)
        #commit transaction
            self.db.commit()
            
        #refresh with relations
            self.db.refresh(pereval)
            return pereval
        
        except SQLalchemyError as e:
            self.db.rollback()
            raise
        except Exception as e:
            self.db.rollback()
            raise
        
    def update_status(self, pereval_id: int, new_status: str) -> Optional[models.Pereval]:
        #Обновляет статус перевала, если текущий статус == "new", иначе возвращает объект без изменений
        obj = self.repo.get_by_id(pereval_id)
        if not obj:
            return None
        if obj.status != "new":
            #не обновляем статус, возвращаем объект без изменений
            return obj
        try:
            obj.status = new_status
            updated = self.repo.update(obj)
            return updated
        except SQLalchemyError:
            self.db.rollback()
            raise
        
