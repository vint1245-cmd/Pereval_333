# app/models/user.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(50), nullable=True)
    fam = Column(String(100), nullable=False)
    name = Column(String(100), nullable=False)
    otc = Column(String(100), nullable=True)

    perevals = relationship(
        "Pereval",
        back_populates="user",
        lazy="selectin"
    )
