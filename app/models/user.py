from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Integer, String, Boolean, DateTime, text
from sqlalchemy.dialects.oracle import RAW
from datetime import datetime

class ZTBL_User(SQLModel, table=True):
    __tablename__ = "app_users"

    id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, primary_key=True, autoincrement=True)
    )
    email: str = Field(
        sa_column=Column(String(255), nullable=False, unique=True, index=True)
    )

    hashed_password: str = Field(
        sa_column=Column(String(255), nullable=False)
    )
    
    is_active: bool = Field(
        sa_column=Column(Boolean, default=True, nullable=False)
    )
    is_locked: bool = Field(
        sa_column=Column(Boolean, default=False, nullable=False)
    )
    created_at: Optional[datetime] = Field(
        sa_column=Column(
            DateTime(timezone=False), 
            server_default=text("CURRENT_TIMESTAMP"),
            nullable=False
        )
    )
    