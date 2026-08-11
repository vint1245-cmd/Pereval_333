# app/services/submit_service.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from app.models.user import User
from app.models.coords import Coords
from app.models.level import Level
from app.models.image import Image
from app.models.pereval import Pereval

from app.schemas.pereval import PerevalCreate, PerevalOut, PerevalUpdate


class SubmitService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_pereval(self, data: PerevalCreate):
        # USER
        user_data = data.user
        q = select(User).where(User.email == user_data.email)
        res = await self.session.execute(q)
        user = res.scalars().first()

        if not user:
            user = User(
                email=user_data.email,
                fam=user_data.fam,
                name=user_data.name,
                otc=user_data.otc,
                phone=user_data.phone
            )
            self.session.add(user)
            await self.session.flush()

        # COORDS
        coords_data = data.coords
        coords = Coords(
            latitude=coords_data.latitude,
            longitude=coords_data.longitude,
            height=coords_data.height
        )
        self.session.add(coords)
        await self.session.flush()

        # LEVEL
        level_data = data.level
        level = Level(
            winter=level_data.winter,
            summer=level_data.summer,
            autumn=level_data.autumn,
            spring=level_data.spring,
        )
        self.session.add(level)
        await self.session.flush()

        # PEREVAL
        pereval_data = {
            "beauty_title": data.beauty_title,
            "title": data.title,
            "other_titles": data.other_titles,
            "connect": data.connect,
            "user_id": user.id,
            "coords_id": coords.id,
            "level_id": level.id,
            "status": "new",
        }
        if data.add_time is not None:
            pereval_data["add_time"] = data.add_time

        pereval = Pereval(**pereval_data)
        self.session.add(pereval)
        await self.session.flush()

        # IMAGES
        for img in data.images:
            image = Image(
                pereval_id=pereval.id,
                title=img.title,
                data=img.data
            )
            self.session.add(image)

        try:
            await self.session.commit()
            await self.session.refresh(pereval)
        except Exception:
            await self.session.rollback()
            raise

        return {
            "status": 200,
            "message": None,
            "id": pereval.id
        }

    async def get_pereval(self, pereval_id: int):
        q = select(Pereval).options(
            selectinload(Pereval.user),
            selectinload(Pereval.coords),
            selectinload(Pereval.level),
            selectinload(Pereval.images),
        ).where(Pereval.id == pereval_id)
        res = await self.session.execute(q)
        obj = res.scalars().first()
        if not obj:
            raise HTTPException(status_code=404, detail=f"Перевал с ID {pereval_id} не найден")
        return PerevalOut.model_validate(obj)

    async def list_by_user_email(self, email: str):
        q = (
            select(Pereval)
            .options(
                selectinload(Pereval.user),
                selectinload(Pereval.coords),
                selectinload(Pereval.level),
                selectinload(Pereval.images),
            )
            .join(User)
            .where(User.email == email)
            .order_by(Pereval.add_time.desc())
        )
        res = await self.session.execute(q)
        objs = res.scalars().all()
        return [PerevalOut.model_validate(o) for o in objs]

    async def update_status(self, pereval_id: int, new_status: str):
        q = select(Pereval).where(Pereval.id == pereval_id)
        res = await self.session.execute(q)
        obj = res.scalars().first()

        if not obj:
            raise HTTPException(status_code=404, detail="Not found")

        if obj.status != "new":
            raise HTTPException(status_code=409, detail="Only records with status 'new' can be updated")

        obj.status = new_status
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)

        return {"state": new_status, "message": "status updated"}

    async def update_pereval(self, pereval_id: int, data: PerevalUpdate):
        q = select(Pereval).options(
            selectinload(Pereval.coords),
            selectinload(Pereval.level),
            selectinload(Pereval.images),
        ).where(Pereval.id == pereval_id)
        res = await self.session.execute(q)
        obj = res.scalars().first()

        if not obj:
            raise HTTPException(status_code=404, detail="Not found")

        if obj.status != "new":
            raise HTTPException(status_code=409, detail="Only records with status 'new' can be updated")

        if data.user is not None:
            if (
                data.user.email != obj.user.email
                or data.user.fam != obj.user.fam
                or data.user.name != obj.user.name
                or data.user.otc != obj.user.otc
                or data.user.phone != obj.user.phone
            ):
                raise HTTPException(status_code=400, detail="User fields cannot be edited")

        if data.beauty_title is not None:
            obj.beauty_title = data.beauty_title
        if data.title is not None:
            obj.title = data.title
        if data.other_titles is not None:
            obj.other_titles = data.other_titles
        if data.connect is not None:
            obj.connect = data.connect
        if data.add_time is not None:
            obj.add_time = data.add_time

        if data.coords is not None:
            obj.coords.latitude = data.coords.latitude
            obj.coords.longitude = data.coords.longitude
            obj.coords.height = data.coords.height

        if data.level is not None:
            obj.level.winter = data.level.winter
            obj.level.summer = data.level.summer
            obj.level.autumn = data.level.autumn
            obj.level.spring = data.level.spring

        if data.images_to_delete:
            delete_ids = set(data.images_to_delete)
            for image in list(obj.images):
                if image.id in delete_ids:
                    await self.session.delete(image)

        if data.images:
            for image_data in data.images:
                image = Image(
                    pereval_id=obj.id,
                    title=image_data.title,
                    data=image_data.data,
                )
                self.session.add(image)

        self.session.add(obj)
        try:
            await self.session.commit()
            await self.session.refresh(obj)
        except Exception:
            await self.session.rollback()
            raise

        return {"state": 1, "message": "Запись успешно отредактирована"}
