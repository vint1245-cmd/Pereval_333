# app/models/pereval.py
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship

from app.db import Base


class Pereval(Base):
    __tablename__ = "perevals"

    id = Column(Integer, primary_key=True, index=True)
    beauty_title = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    other_titles = Column(Text, nullable=True)
    connect = Column(Text, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    coords_id = Column(Integer, ForeignKey("coords.id"), nullable=False)
    level_id = Column(Integer, ForeignKey("levels.id"), nullable=False)

    status = Column(String(20), default="new", nullable=False)
    add_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Связи. Используем back_populates для двунаправленной навигации
    user = relationship("User", back_populates="perevals")
    coords = relationship("Coords", back_populates="perevals")
    level = relationship("Level", back_populates="perevals")
    images = relationship(
        "Image",
        back_populates="pereval",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
