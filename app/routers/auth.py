from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlmodel import Session

from ..database.db import get_session
from ..core.security import authenticate_user, create_access_token, verify_otp
from ..core.config import settings

router = APIRouter()

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    otp: str = Form(...),
    session: Session = Depends(get_session),
):
    user = authenticate_user(session, form_data.username, form_data.password)
    is_valid_otp = verify_otp(otp)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not is_valid_otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect OTP",
        )
    access_token = create_access_token(data={"sub": user.email})
    return Token(access_token=access_token)
