# app/models/coords.py
from sqlalchemy import Column, Integer, Float
from sqlalchemy.orm import relationship

from app.db import Base


class Coords(Base):
    __tablename__ = "coords"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    height = Column(Integer, nullable=False)

    # связь с Pereval
    perevals = relationship("Pereval", back_populates="coords", lazy="selectin")
