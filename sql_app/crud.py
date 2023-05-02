from sqlalchemy.orm import Session
from . import models, schemas
import numpy_financial as npf

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email,
                          first_name=user.first_name,
                          last_name=user.last_name,
                          creation_date=user.creation_date,
                          birth_date=user.birth_date,
                          hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_user_loan(db: Session, loan: schemas.LoanCreate, user_id: int):
    db_loan = models.Item(**loan.dict(), owner_id=user_id)
    schedule = create_loan_schedule(db, db_loan)
    db_loan.loan_schedule = schedule
#     print(db_loan.summary)
#     print(db_loan)
#     db_loan_schedule = db_loan.loan_schedule
#     db_loan_schedule.append()
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

def get_all_user_loans(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    return db_user.loans

def get_loans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

def create_loan_schedule(db: Session, loan: models.Item):
    schedule = {}
    for month in range(1, loan.loan_terms_months + 1):
        summary = calculate_month_summary(loan, month)
        schedule[month] = summary
    return schedule

def calculate_month_summary(loan: models.Item, month: int):
    principal_amount = loan.amount
    rate = loan.annual_interest_rate
    term = loan.loan_terms_months

    monthly_payment = float(f"{npf.pmt((rate/12), term, -principal_amount):.2f}")
    interest_paid = float(f"{npf.ipmt((rate/12), month, term, -principal_amount):.2f}")
    principal_paid = float(f"{npf.ppmt((rate/12), month, term, -principal_amount):.2f}")

    return schemas.LoanSummary(current_principal = principal_amount,
                               principal_paid = principal_paid,
                               interest_paid = interest_paid,
                               remaining_balance = (principal_amount-principal_paid),
                               monthly_payment = monthly_payment)
