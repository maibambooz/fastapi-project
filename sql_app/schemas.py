from pydantic import BaseModel, EmailStr, PositiveFloat, conint, confloat, validator
from typing import Dict
from datetime import datetime, date
from pydantic import constr
import re

class LoanBase(BaseModel):
    amount: confloat(ge=1) = 1.00
    annual_interest_rate: confloat(gt=1) = 1.00
    loan_terms_months: conint(gt=1) = 1

class LoanCreate(LoanBase):
    pass

class LoanSummary(BaseModel):
    current_principal: float
    principal_paid: float
    interest_paid: float
    remaining_balance: float
    monthly_payment: float

class Loan(LoanBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: EmailStr
    first_name: constr(regex="^[a-zA-Z]{2,}$") = 'John'
    last_name: constr(regex="^[a-zA-Z]{2,}$") = 'Smith'
    creation_date: date
    birth_date: date

class UserCreate(UserBase):
    password: str = "passwordtest123-_"

    @validator('password')
    def password_cannot_contain_space(cls, value):
        if not re.match("^[A-Za-z0-9_-]{8,}$", value):
            raise ValueError('Password must be a length of 8 characters or more, containing letters, numbers, dashes and underscores.')
        return value.title()

class User(UserBase):
    id: int
    is_active: bool
    loans: list[Loan] = []

    class Config:
        orm_mode = True
