# app/models/image.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    pereval_id = Column(Integer, ForeignKey("perevals.id", ondelete="CASCADE"), nullable=False)
    data = Column(String, nullable=False)  # base64 строка
    title = Column(String(255), nullable=True)

    pereval = relationship("Pereval", back_populates="images")
