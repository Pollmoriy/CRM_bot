from sqlalchemy import Column, Integer, String, Enum
from database.db import Base
import enum

class UserRole(enum.Enum):
    admin = "Admin"
    manager = "Manager"
    user = "User"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    full_name = Column(String(100))
    phone = Column(String(20))
    telegram_id = Column(String(50))
    role = Column(Enum(UserRole))
    hashed_password = Column(String(255))
