# app/models/level.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Level(Base):
    __tablename__ = "levels"

    id = Column(Integer, primary_key=True, index=True)
    winter = Column(String(10), nullable=True)
    summer = Column(String(10), nullable=True)
    autumn = Column(String(10), nullable=True)
    spring = Column(String(10), nullable=True)

    # связь с Pereval
    perevals = relationship("Pereval", back_populates="level", lazy="selectin")
