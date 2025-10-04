# database/models.py
from peewee import *
from database.db import db
from datetime import datetime

class BaseModel(Model):
    class Meta:
        database = db


# Пользователи
class User(BaseModel):
    tg_id = BigIntegerField(unique=True)
    full_name = CharField(null=True)
    phone = CharField(null=True)
    email = CharField(null=True)
    role = CharField(default='user', choices=[('user', 'User'), ('manager', 'Manager'), ('admin', 'Admin')])
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)


# Клиенты
class Client(BaseModel):
    name = CharField()
    phone = CharField(null=True)
    email = CharField(null=True)
    company = CharField(null=True)
    note = TextField(null=True)
    created_by = ForeignKeyField(User, backref='clients', null=True)
    created_at = DateTimeField(default=datetime.now)
    manager = ForeignKeyField(User, backref='clients_managed', null=True)


# Сделки
class Deal(BaseModel):
    client = ForeignKeyField(Client, backref='deals')
    title = CharField()
    amount = DecimalField(null=True, max_digits=12, decimal_places=2)
    status = CharField(default='open')  # open, won, lost
    created_at = DateTimeField(default=datetime.now)
    assigned_to = ForeignKeyField(User, backref='deals_assigned', null=True)


# Задачи
class Task(BaseModel):
    title = CharField()
    description = TextField(null=True)
    due_date = DateTimeField(null=True)
    client = ForeignKeyField(Client, backref='tasks', null=True)
    assigned_to = ForeignKeyField(User, backref='tasks', null=True)
    status = CharField(default='todo')  # todo, in_progress, done
    reminder_sent = BooleanField(default=False)
    created_at = DateTimeField(default=datetime.now)

# Напоминания
class Reminder(BaseModel):
    task = ForeignKeyField(Task, backref='reminders')
    remind_at = DateTimeField()
    sent = BooleanField(default=False)

# Логи действий
class ActivityLog(BaseModel):
    user = ForeignKeyField(User, null=True)
    action = TextField()
    created_at = DateTimeField(default=datetime.now)
    assigned_to = ForeignKeyField(User, backref='deals_assigned', null=True)


# Вложения
class Attachment(BaseModel):
    client = ForeignKeyField(Client, backref='attachments', null=True)
    deal = ForeignKeyField(Deal, backref='attachments', null=True)
    file_path = CharField()
    description = TextField(null=True)
    uploaded_at = DateTimeField(default=datetime.now)

# Настройки
class Setting(BaseModel):
    user = ForeignKeyField(User, backref='settings', null=True)
    key = CharField()
    value = CharField()
    updated_at = DateTimeField(default=datetime.now)

# История сообщений
class MessageHistory(BaseModel):
    user = ForeignKeyField(User, backref='messages', null=True)
    message = TextField()
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
