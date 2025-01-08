from peewee import *
from conf.conf import conf

db = MySQLDatabase(
    conf.mysql.database,
    user=conf.mysql.user,
    password=conf.mysql.password,
    host=conf.mysql.host,
    port=conf.mysql.port
)

class BaseModel(Model):
    class Meta:
        database = db

