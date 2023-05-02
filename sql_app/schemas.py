from pydantic import BaseModel, ValidationError, validator
from typing import Dict
from datetime import datetime, date

class LoanBase(BaseModel):
    amount: int
    annual_interest_rate: float
    loan_terms_months: int                  

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
    loan_schedule: Dict[int, LoanSummary] = {}

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
