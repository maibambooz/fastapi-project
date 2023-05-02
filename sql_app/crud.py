from sqlalchemy.orm import Session
from . import models, schemas
import numpy_financial as npf

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
    db_loan.loan_schedule = create_loan_schedule(db, db_loan)
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
    return db.query(models.User).offset(skip).limit(limit).all()

"""
    get_all_user_loans() retrieves all loans under specified user
    Parameters
    ---
    db: Session, required
        Reference to the current database session storing the data
    user_id: int, required
        Integer value that represents user identification number
"""
def get_all_user_loans(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    return db_user.loans

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
    db_user = crud.get_user(db, user_id=user_id)
    db_loans = crud.get_all_user_loans(db, user_id=user_id)
    # Iterate through all user loans, find matching loan_id
    for loan in db_loans:
        if loan.id == loan_id:
            db_schedule = loan.loan_schedule
            break
    if db_schedule is None:
        raise HTTPException(status_code=404, detail="Specified loan cannot be found")
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
    db_schedule = get_loan_schedule(db,user_id=user_id, loan_id=loan_id)
    try:
        loan_summary = db_schedule[month]
        return loan_summary
    except KeyError:
        raise HTTPException(status_code=400, detail="Monthly summary cannot be retrieved")


def share_loan(db: Session, user_id: int, other_user_id, loan_id: int):
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