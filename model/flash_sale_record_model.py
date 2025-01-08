from peewee import AutoField, ForeignKeyField, DateTimeField, SQL
from base_model import BaseModel
from model.flash_sale_model import FlashSale
from model.user_model import Users


class FlashSaleRecords(BaseModel):
    record_id = AutoField()
    user = ForeignKeyField(Users, backref='flash_sale_records')
    sale = ForeignKeyField(FlashSale, backref='flash_sale_records')
    created_at = DateTimeField(constraints=[SQL('DEFAULT CURRENT_TIMESTAMP')])

    class Meta:
        indexes = (
            (('user', 'sale'), True),  # 确保用户对每个秒杀活动只能参与一次
        )