# database/db.py
from peewee import MySQLDatabase
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

db = MySQLDatabase(
    DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    charset='utf8mb4'
)
