from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel, EmailStr

from ..models.user import User1
from ..core.security import get_current_user
from ..database.db import get_session
from ..core.security import get_password_hash

router = APIRouter()

class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        from_attributes = True




@router.get("/me", response_model=UserOut)
def read_me(current_user: User1 = Depends(get_current_user)):
    return current_user


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_in: UserCreate, session: Session = Depends(get_session)):
    # check if email already exists
    existing = session.exec(
        select(User1).where(User1.email == user_in.email)
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    db_user = User1(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
