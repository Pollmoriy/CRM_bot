import re
from database.models import User
from database.db import db

def is_valid_email(email: str) -> bool:
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not bool(re.match(pattern, email)):
        return False

    # Проверка на уникальность email
    db.connect(reuse_if_open=True)
    exists = User.select().where(User.email == email).exists()
    db.close()

    return not exists

def is_valid_phone(phone: str) -> bool:
    pattern = r'^\+?\d{10,15}$'
    if not bool(re.match(pattern, phone)):
        return False

        # Проверка на уникальность телефона
    db.connect(reuse_if_open=True)
    exists = User.select().where(User.phone == phone).exists()
    db.close()

    return not exists
