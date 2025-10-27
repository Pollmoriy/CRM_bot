# database/models.py
from peewee import *
from .db import db

class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    id_user = AutoField(primary_key=True)
    full_name = CharField(max_length=100)
    phone = CharField(max_length=20, null=True)
    telegram_id = CharField(max_length=50, unique=True)
    role = CharField(max_length=20, default='employee')
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])
