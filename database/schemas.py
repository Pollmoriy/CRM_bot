from pydantic import BaseModel, validator
from typing import Optional
from enum import Enum
import re

class UserRole(str, Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"

class UserCreate(BaseModel):
    full_name: str
    phone: Optional[str] = None
    telegram_id: str

    @validator('full_name')
    def validate_full_name(cls, v):
        # Проверяем, что только буквы и пробелы
        if not re.match(r"^[А-Яа-яA-Za-zЁё\s'-]+$", v):
            raise ValueError("ФИО должно содержать только буквы, пробелы или дефисы")
        # Проверяем, что минимум 2 слова
        if len(v.strip().split()) < 2:
            raise ValueError("ФИО должно состоять минимум из 2 слов")
        return v
