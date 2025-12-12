from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer, String, Identity

class ZTBL_User(SQLModel, table=True):
    __tablename__ = "ztbl_user2"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(
            Integer,
            Identity(start=1, increment=1),
            primary_key=True,
        ),
    )
    email: str = Field(
        sa_column=Column(String(255), nullable=False, unique=True, index=True)
    )

    hashed_password: str = Field(
        sa_column=Column(String(255), nullable=False)
    )
