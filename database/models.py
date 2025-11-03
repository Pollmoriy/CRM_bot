# database/models.py (фрагмент)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, Enum, func
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    admin = "admin"
    manager = "manager"
    employee = "employee"

class User(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    telegram_id = Column(String(50))
    role = Column(Enum(UserRole), nullable=False, default=UserRole.employee)
    created_at = Column(TIMESTAMP, server_default=func.current_timestamp())
    manager_id = Column(Integer)  # FK уже в БД, SQLAlchemy можно добавить ForeignKey при желании

    def __repr__(self):
        return f"<User(id={self.id_user}, name={self.full_name})>"

class Client(Base):
    __tablename__ = 'clients'

    id_client = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20))
    telegram = Column(String(50))
    birth_date = Column(Date)
    added_date = Column(TIMESTAMP, server_default=func.now())
    segment = Column(Enum('new', 'regular', 'vip'), default='new')
    notes = Column(Text)
