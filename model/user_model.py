from peewee import AutoField, CharField, DateTimeField, SQL
from model.base_model import BaseModel

class Users(BaseModel):
    user_id = AutoField()
    username = CharField(unique=True)
    password_hash = CharField()
    email = CharField(unique=True)
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

