from sqlalchemy import Boolean, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    creation_date = Column(Date)
    birth_date = Column(Date)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    loans = relationship("Item", back_populates="owner")

class Item(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)
    annual_interest_rate = Column(Float)
    loan_terms_months = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="loans")