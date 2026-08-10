from sqlalchemy.orm import Session
from app.models.user import User
from app.models.coords import Coords
from app.models.level import Level
from app.models.pereval import Pereval
from app.models.image import Image
from app.schemas.pereval import PerevalCreate


def create_pereval_repo(db: Session, payload: PerevalCreate) -> Pereval:
    # User: ищем по email, если нет — создаём
    user = db.query(User).filter(User.email == payload.user.email).first()
    if not user:
        user = User(
            email=payload.user.email,
            phone=payload.user.phone,
            fam=payload.user.fam,
            name=payload.user.name,
            otc=payload.user.otc,
        )
        db.add(user)
        db.flush()

    coords = Coords(
        latitude=payload.coords.latitude,
        longitude=payload.coords.longitude,
        height=payload.coords.height,
    )
    db.add(coords)
    db.flush()

    level = Level(
        winter=payload.level.winter,
        summer=payload.level.summer,
        autumn=payload.level.autumn,
        spring=payload.level.spring,
    )
    db.add(level)
    db.flush()

    pereval = Pereval(
        beauty_title=payload.beauty_title,
        title=payload.title,
        other_titles=payload.other_titles,
        connect=payload.connect,
        user_id=user.id,
        coords_id=coords.id,
        level_id=level.id,
    )
    db.add(pereval)
    db.flush()

    for img in payload.images:
        image = Image(
            pereval_id=pereval.id,
            data=img.data,
            title=img.title,
        )
        db.add(image)

    db.commit()
    db.refresh(pereval)
    return pereval

def get_pereval_by_id_repo(db: Session, pereval_id: int) -> Pereval | None:
    return db.query(Pereval).filter(Pereval.id == pereval_id).first()
        
def update_pereval_repo(db: Session, pereval: Pereval, payload):
    # Обновляем простые поля
    pereval.beauty_title = payload.beauty_title
    pereval.title = payload.title
    pereval.other_titles = payload.other_titles
    pereval.connect = payload.connect

    # Обновляем coords
    pereval.coords.latitude = payload.coords.latitude
    pereval.coords.longitude = payload.coords.longitude
    pereval.coords.height = payload.coords.height

    # Обновляем level
    pereval.level.winter = payload.level.winter
    pereval.level.summer = payload.level.summer
    pereval.level.autumn = payload.level.autumn
    pereval.level.spring = payload.level.spring

    # Удаляем старые images
    db.query(Image).filter(Image.pereval_id == pereval.id).delete()

    # Добавляем новые images
    for img in payload.images:
        new_img = Image(
            pereval_id=pereval.id,
            data=img.data,
            title=img.title
        )
        db.add(new_img)

    db.commit()
    db.refresh(pereval)

    return pereval
    