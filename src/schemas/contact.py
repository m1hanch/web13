from typing import Optional

from pydantic import BaseModel, EmailStr, Field, PastDate
from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(max_length=17, min_length=9)
    birthday: PastDate
    other: Optional[str]


class ContactResponse(BaseModel):
    id: int = 1
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthday: PastDate
    other: str
    user: UserResponse | None

    class Config:
        from_attributes = True
