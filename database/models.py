# database/models.py (фрагмент)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text, Date, TIMESTAMP, Enum, ForeignKey, Boolean, func, DateTime
from sqlalchemy.orm import relationship
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

# 1️⃣ Этапы сделки (для удобства при отображении)
class DealStage(enum.Enum):
    new = "Новая"
    in_progress = "В работе"
    completed = "Закрыта"
    on_hold = "Приостановлена"


class Deal(Base):
    __tablename__ = "deals"

    id_deal = Column(Integer, primary_key=True, autoincrement=True)
    deal_name = Column(String(150), nullable=False)

    id_client = Column(Integer, ForeignKey("clients.id_client", ondelete="SET NULL"))
    id_manager = Column(Integer, ForeignKey("users.id_user", ondelete="SET NULL"))

    progress = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)

    stage = Column(
        Enum(DealStage, values_callable=lambda obj: [e.value for e in obj]),
        default=DealStage.new.value,
        nullable=False
    )

    date_created = Column(TIMESTAMP, server_default=func.current_timestamp())
    date_completed = Column(Date)

    client = relationship("Client", backref="deals")
    manager = relationship("User", backref="deals", foreign_keys=[id_manager])
    tasks = relationship("Task", back_populates="deal", cascade="all, delete-orphan")



# 2️⃣ Статусы и приоритеты задач
class TaskStatus(enum.Enum):
    new = "new"
    in_progress = "in_progress"
    done = "done"
    overdue = "overdue"


class TaskPriority(enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(Base):
    __tablename__ = "tasks"

    id_task = Column(Integer, primary_key=True, autoincrement=True)
    task_name = Column(String(150), nullable=False)
    description = Column(Text)

    id_employee = Column(Integer, ForeignKey("users.id_user", ondelete="SET NULL"))
    id_deal = Column(Integer, ForeignKey("deals.id_deal", ondelete="SET NULL"))

    status = Column(Enum(TaskStatus), default=TaskStatus.new)
    priority = Column(Enum(TaskPriority), default=TaskPriority.medium)

    deadline = Column(Date)
    date_completed = Column(Date)

    # связи
    employee = relationship("User", backref="tasks", foreign_keys=[id_employee])
    deal = relationship("Deal", back_populates="tasks")

    def __repr__(self):
        return f"<Task(id={self.id_task}, name={self.task_name}, status={self.status.value})>"

class AuditLog(Base):
    __tablename__ = "auditlogs"

    id_log = Column(Integer, primary_key=True, autoincrement=True)
    id_user = Column(Integer, ForeignKey("users.id_user", ondelete="SET NULL"))
    table_name = Column(String(50))
    action = Column(Enum("insert", "update", "delete"))
    record_id = Column(Integer)
    action_time = Column(DateTime)
    details = Column(Text)

    # <-- добавляем отношение
    user = relationship("User", backref="auditlogs")
