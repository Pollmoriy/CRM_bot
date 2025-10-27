from passlib.context import CryptContext

# Контекст для bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Хэширование пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Проверка пароля
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed)
