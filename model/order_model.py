from peewee import AutoField, CharField, DateTimeField, ForeignKeyField, SQL
from base_model import BaseModel
from model.flash_sale_model import FlashSale
from model.product_model import Product
from model.user_model import Users


class Orders(BaseModel):
    order_id = AutoField()
    user = ForeignKeyField(Users, backref='orders')
    product = ForeignKeyField(Product, backref='orders')
    sale = ForeignKeyField(FlashSale, backref='orders')
    order_status = CharField(choices=[('PENDING', '待处理'), ('COMPLETED', '已完成'), ('CANCELLED', '已取消')], default='PENDING')
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])