import re

def is_valid_email(email: str) -> bool:
    """Проверяет корректность email"""
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return bool(re.match(pattern, email))

def is_valid_phone(phone: str) -> bool:
    """Проверяет корректность номера телефона (только цифры, 10-15 символов)"""
    pattern = r'^\+?\d{10,15}$'
    return bool(re.match(pattern, phone))
