from peewee import AutoField, ForeignKeyField, DateTimeField, IntegerField, SQL
from base_model import BaseModel
from model.product_model import Products


class FlashSales(BaseModel):
    sale_id = AutoField()
    product = ForeignKeyField(Products, backref='flash_sales')
    start_time = DateTimeField()
    end_time = DateTimeField()
    total_stock = IntegerField()  # 秒杀总库存
    sold = IntegerField(default=0)  # 已售数量
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])