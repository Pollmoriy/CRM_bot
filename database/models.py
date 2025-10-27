from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base
import enum

class UserRole(enum.Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"

class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    telegram_id = Column(String(50))
    role = Column(Enum(UserRole), default=UserRole.employee)
    manager_id = Column(Integer, ForeignKey("users.id_user"), nullable=True)  # <- связь

    manager = relationship("User", remote_side=[id_user], backref="subordinates")
