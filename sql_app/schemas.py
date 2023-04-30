from pydantic import BaseModel, ValidationError, validator
from datetime import datetime, date

class loanBase(BaseModel):
    title: str
    amount: int
    annual_interest_rate: float
    loan_terms_months: int
    #description: str | None = None


class loanCreate(loanBase):
    pass


class Loan(loanBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str
    first_name: str
    last_name: str
    creation_date: date
    birth_date: date


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    is_active: bool
    loans: list[Loan] = []

    class Config:
        orm_mode = True