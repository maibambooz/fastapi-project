from pydantic import BaseModel, ValidationError, validator
# from typing import List
from datetime import datetime, date

# class LoanBase(BaseModel):
# #     amount: int
# #     annual_interest_rate: float
# #     loan_terms_months: int
#
# # class loan_schedule(BaseModel):
# #     month: str
# #     remaining_balance: float
# #     monthly_payment: float

class LoanBase(BaseModel):
    title: str
    description: str | None = None

class LoanCreate(LoanBase):
    pass

class Loan(LoanBase):
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