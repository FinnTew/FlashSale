from peewee import AutoField, CharField, DecimalField, IntegerField, TextField, DateTimeField, SQL
from base_model import BaseModel

class Products(BaseModel):
    product_id = AutoField()
    name = CharField()
    description = TextField(null=True)
    price = DecimalField(max_digits=10, decimal_places=2)
    stock = IntegerField()  # 初始库存
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])