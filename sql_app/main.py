from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@app.get("/users/", response_model=list[schemas.User])
def get_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.post("/users/{user_id}/loans/", response_model=schemas.Loan)
def create_user_loan(loan: schemas.LoanCreate, user_id: int, db: Session = Depends(get_db)):
    return crud.create_user_loan(db=db, loan=loan, user_id=user_id)

@app.get("/loans/", response_model=schemas.Loan)
def get_all_loans(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    loans = crud.get_loans(db, skip=skip, limit=limit)
    return loans

@app.get("/users/{user_id}/loans", response_model=list[schemas.Loan])
def get_all_user_loans(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_all_user_loans(db, user_id=user_id)
    return db_user

@app.get("/users/{user_id}/loans/{loan_id}")
def get_loan_schedule(user_id: int, loan_id: int, db: Session = Depends(get_db)):
    db_schedule = get_loan_schedule(db,user_id=user_id, loan_id=loan_id)
    return db_schedule

@app.get("/users/{user_id}/loans/{loan_id}/{month}")
def get_loan_summary(user_id: int, loan_id: int, month: int, db: Session = Depends(get_db)):
    db_loan_summary = get_loan_summary(db, user_id=user_id, loan_id=loan_id, month=month)
    return db_loan_summary