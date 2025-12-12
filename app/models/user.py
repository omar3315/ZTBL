from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import String  # important

class ZTBL_User(SQLModel, table=True):
    __tablename__ = "ztbl_user"  # matches the table name in the error

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(sa_column_kwargs={"type_": String(255)})
    hashed_password: str = Field(sa_column_kwargs={"type_": String(255)})
