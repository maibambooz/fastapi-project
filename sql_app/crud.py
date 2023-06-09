from sqlalchemy.orm import Session
from . import models, schemas
from passlib.context import CryptContext
from fastapi import FastAPI, HTTPException
import numpy_financial as npf

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
"""
    create_user() create new user
    Parameters
    ---
    db: Session, required
        Reference to the current database session storing the data
    user: schemas.UserCreate, required
        Schema of User object to be used to populate information
"""
def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = password_context.hash(user.password)
    db_user = models.User(email=user.email,
                          first_name=user.first_name,
                          last_name=user.last_name,
                          creation_date=user.creation_date,
                          birth_date=user.birth_date,
                          hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

"""
    create_user_loan() create new loan under specified user
    Parameters
    ---
    db: Session, required
        Reference to the current database session storing the data
    loan: schemas.LoanCreate, required
        Schema of Loan object to be used to populate information
    user_id: int, required
            Integer value that represents user identification number
"""
def create_user_loan(db: Session, loan: schemas.LoanCreate, user_id: int):
    db_loan = models.Item(**loan.dict(), owner_id=user_id)
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan

"""
    create_loan_schedule() create loan schedule that contains all loan term monthly summary
    Parameters
    ---
    db: Session, required
        Reference to the current database session storing the data
    loan: models.Item, required
        Model of class Item to be used to obtain loan information
"""
def create_loan_schedule(db: Session, loan: models.Item):
    schedule = {}
    for month in range(1, loan.loan_terms_months + 1):
        summary = calculate_month_summary(loan, month)
        schedule[month] = summary
    return schedule

"""
    get_user() retrieves user using user_id
    Parameters
    ---
    db: Session, required
        Reference to the current database session storing the data
    user_id: int, required
        Integer value that represents user identification number
"""
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

"""
    get_user_by_email() retrieves user using their email
    Parameters
    ---
    db: Session, required
        Reference to the current database session storing the data
    email: str, required
        String value that contains email information
"""
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

"""
    get_users() retrieves all users within database
    Parameters
    ---
    db: Session, required
        Reference to the current database session storing the data
    skip: int, default 0
        Integer value to specify how many records to skip
    limit: int, default 100
        Integer value to limit the number of records
"""
def get_users(db: Session, skip: int = 0, limit: int = 100):
    db_user = db.query(models.User).offset(skip).limit(limit).all()
    return db_user

"""
    get_loans() retrieves all loans within database
    Parameters
    ---
    db: Session, required
        Reference to the current database session storing the data
    skip: int, default 0
        Integer value to specify how many records to skip
    limit: int, default 100
        Integer value to limit the number of records
"""
def get_loans(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()

"""
    get_loan_schedule() retrieves specific loan schedule under specified user and loan_id
    Parameters
    ---
    db: Session, required
        Reference to the current database session storing the data
    user_id: int, required
        Integer value that represents user identification number
    loan_id: int, required
        Integer value that represents user's loan identification number
"""
def get_loan_schedule(db: Session, user_id: int, loan_id: int):
    db_user = get_user(db, user_id)
    db_loans = db_user.loans
    # Iterate through all user loans, find matching loan_id
    for loan in db_loans:
        if loan.id == loan_id:
            db_schedule = create_loan_schedule(db, loan)
            break
        else:
            raise HTTPException(status_code=400, detail="User loan cannot be found. Loan ID is: {}".format(loan_id))
    return db_schedule

"""
    get_loan_summary() retrieves specified month loan summary under specified user and loan_id
    Parameters
    ---
    db: Session, required
        Reference to the current database session storing the data
    user_id: int, required
        Integer value that represents user identification number
    loan_id: int, required
        Integer value that represents user's loan identification number
    month: int, required
        Integer value between the numbers of 1-12 for months
"""
def get_loan_summary(db: Session, user_id: int, loan_id: int, month: int):
    db_schedule = get_loan_schedule(db, user_id=user_id, loan_id=loan_id)

    if month > len(db_schedule):
        raise HTTPException(status_code=400, detail="Specified month exceeds the loan term. Loan term is: {}".format(len(db_schedule)))

    loan_summary = db_schedule[month]
    return loan_summary

"""
    Due to time constraints on my end, I will not have enough time to implement the share loan functionality
    Thoughts of process:
        - Obtain id number of both owner and other owner
        - Retrieve loan using loan id
        - Most likely within the User class, I would add in a list[Loan] field called co-signers
        - Once we retrieve the loan object, we simply add it onto the other user list
"""
def share_loan(db: Session, user_id: int, other_user_id, loan_id: int):
    db_user = get_user(db, user_id)
    db_other_user = get_user(db, user_id)

    if db_user is None or db_other_user is None:
        raise HTTPException(status_code=404, detail="User(s) cannot be found")


    return None

"""
    calculate_month_summary() takes in loan object and specified month needed for calculations
    Parameters
    ---

    loan: models.Item, required
        Loan object that contains amount, rate and term length
    month: int, required
        Integer value between the numbers of 1-12 for months
"""
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