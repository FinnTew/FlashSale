from peewee import AutoField, CharField, DateTimeField, ForeignKeyField, SQL
from base_model import BaseModel
from model.flash_sale_model import FlashSales
from model.product_model import Products
from model.user_model import Users


class Orders(BaseModel):
    order_id = CharField(unique=True, primary_key=True)
    user = ForeignKeyField(Users, backref='orders')
    product = ForeignKeyField(Products, backref='orders')
    sale = ForeignKeyField(FlashSales, backref='orders')
    order_status = CharField(choices=[('PENDING', '待处理'), ('COMPLETED', '已完成'), ('CANCELLED', '已取消')], default='PENDING')
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])


class Orders0(BaseModel):
    order_id = CharField(unique=True, primary_key=True)
    user = ForeignKeyField(Users, backref='orders')
    product = ForeignKeyField(Products, backref='orders')
    sale = ForeignKeyField(FlashSales, backref='orders')
    order_status = CharField(choices=[('PENDING', '待处理'), ('COMPLETED', '已完成'), ('CANCELLED', '已取消')], default='PENDING')
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        table_name = 'orders_0'

class Orders1(BaseModel):
    order_id = CharField(unique=True, primary_key=True)
    user = ForeignKeyField(Users, backref='orders')
    product = ForeignKeyField(Products, backref='orders')
    sale = ForeignKeyField(FlashSales, backref='orders')
    order_status = CharField(choices=[('PENDING', '待处理'), ('COMPLETED', '已完成'), ('CANCELLED', '已取消')], default='PENDING')
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        table_name = 'orders_1'

class Orders2(BaseModel):
    order_id = CharField(unique=True, primary_key=True)
    user = ForeignKeyField(Users, backref='orders')
    product = ForeignKeyField(Products, backref='orders')
    sale = ForeignKeyField(FlashSales, backref='orders')
    order_status = CharField(choices=[('PENDING', '待处理'), ('COMPLETED', '已完成'), ('CANCELLED', '已取消')], default='PENDING')
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        table_name = 'orders_2'

class Orders3(BaseModel):
    order_id = CharField(unique=True, primary_key=True)
    user = ForeignKeyField(Users, backref='orders')
    product = ForeignKeyField(Products, backref='orders')
    sale = ForeignKeyField(FlashSales, backref='orders')
    order_status = CharField(choices=[('PENDING', '待处理'), ('COMPLETED', '已完成'), ('CANCELLED', '已取消')], default='PENDING')
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        table_name = 'orders_3'
