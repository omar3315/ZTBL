from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, String

class ZTBL_User(SQLModel, table=True):
    __tablename__ = "ztbl_user"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(
        sa_column=Column(String(255), nullable=False, unique=True, index=True)
    )
    hashed_password: str = Field(
        sa_column=Column(String(255), nullable=False)
    )
