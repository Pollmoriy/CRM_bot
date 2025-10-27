from pydantic import BaseModel, Field
from typing import Optional

class UserCreate(BaseModel):
    full_name: str = Field(..., min_length=3)
    phone: str
    telegram_id: int
    password: str

class UserRead(BaseModel):
    id: int
    full_name: str
    phone: str
    telegram_id: int
    role: str
