from peewee import *
from database.db import db
from datetime import datetime

class BaseModel(Model):
    class Meta:
        database = db

# Пользователи
class User(BaseModel):
    tg_id = BigIntegerField(unique=True, null=False)
    full_name = CharField(null=True)
    phone = CharField(null=True)
    email = CharField(null=True)
    role = CharField(default='user', choices=[('user', 'User'), ('manager', 'Manager'), ('admin', 'Admin')])
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)

# Клиенты
class Client(BaseModel):
    name = CharField(null=False)
    phone = CharField(null=True)
    email = CharField(null=True)
    company = CharField(null=True)
    note = TextField(null=True)
    created_by = ForeignKeyField(User, backref='clients_created', null=True, on_delete='SET NULL')
    manager = ForeignKeyField(User, backref='clients_managed', null=True, on_delete='SET NULL')
    created_at = DateTimeField(default=datetime.now)

# Сделки
class Deal(BaseModel):
    client = ForeignKeyField(Client, backref='deals', null=False, on_delete='CASCADE')
    title = CharField(null=False)
    amount = DecimalField(null=True, max_digits=12, decimal_places=2)
    status = CharField(default='open', choices=[('open','Open'),('won','Won'),('lost','Lost')])
    assigned_to = ForeignKeyField(User, backref='deals_assigned', null=True, on_delete='SET NULL')
    created_at = DateTimeField(default=datetime.now)

# Задачи
class Task(BaseModel):
    title = CharField(null=False)
    description = TextField(null=True)
    due_date = DateTimeField(null=True)
    client = ForeignKeyField(Client, backref='tasks', null=True, on_delete='SET NULL')
    assigned_to = ForeignKeyField(User, backref='tasks_assigned', null=True, on_delete='SET NULL')
    status = CharField(default='todo', choices=[('todo','Todo'),('in_progress','In Progress'),('done','Done')])
    reminder_sent = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)

# Напоминания
class Reminder(BaseModel):
    task = ForeignKeyField(Task, backref='reminders', null=False, on_delete='CASCADE')
    remind_at = DateTimeField(null=False)
    sent = BooleanField(default=False)

# Логи действий
class ActivityLog(BaseModel):
    user = ForeignKeyField(User, null=True, backref='activities', on_delete='SET NULL')
    action = TextField(null=False)
    created_at = DateTimeField(default=datetime.now)

# Вложения
class Attachment(BaseModel):
    client = ForeignKeyField(Client, backref='attachments', null=True, on_delete='SET NULL')
    deal = ForeignKeyField(Deal, backref='attachments', null=True, on_delete='SET NULL')
    file_path = CharField(null=False)
    description = TextField(null=True)
    uploaded_at = DateTimeField(default=datetime.now)

# Настройки
class Setting(BaseModel):
    user = ForeignKeyField(User, backref='settings', null=False, on_delete='CASCADE')
    key = CharField(null=False)
    value = CharField(null=False)
    updated_at = DateTimeField(default=datetime.now)

# История сообщений
class MessageHistory(BaseModel):
    user = ForeignKeyField(User, backref='messages', null=False, on_delete='CASCADE')
    message = TextField(null=False)
    created_at = DateTimeField(default=datetime.now)

# Инициализация таблиц
def init_db():
    db.connect()
    db.create_tables([
        User, Client, Deal, Task, Reminder, ActivityLog,
        Attachment, Setting, MessageHistory
    ])
    db.close()

if __name__ == "__main__":
    init_db()
    print("Таблицы созданы успешно!")
