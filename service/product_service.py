from model.product_model import Products
import logging

logger = logging.getLogger(__name__)

class ProductService:
    def __init__(self):
        self.product = Products()

    def create_product(self, name: str, description: str, price: float, stock: int) -> bool:
        try:
            self.product.create(
                name=name,
                description=description,
                price=price,
                stock=stock
            )
            return True
        except Exception as e:
            logger.error(f"创建商品失败: {str(e)}")
            return False

    def update_product(self, product_id: int, name: str, description: str, price: float) -> bool:
        try:
            self.product.update(
                name=name,
                description=description,
                price=price
            ).where(Products.product_id == product_id).execute()
            return True
        except Exception as e:
            logger.error(f"更新商品失败: {str(e)}")
            return False

    def get_product_by_id(self, product_id: int):
        return self.product.select().where(Products.product_id == product_id).first()

    def get_all_products(self):
        return self.product.select()

    def delete_product(self, product_id: int) -> bool:
        try:
            self.product.delete().where(Products.product_id == product_id).execute()
            return True
        except Exception as e:
            logger.error(f"删除商品失败: {str(e)}")
            return False

    def decrease_stock(self, product_id: int, amount: int) -> bool:
        product = self.get_product_by_id(product_id)
        if product is None:
            return False
        if product.stock < amount:
            return False
        try:
            self.product.update(
                stock=Products.stock - amount
            ).where(Products.product_id == product_id).execute()
            return True
        except Exception as e:
            logger.error(f"减少库存失败: {str(e)}")
            return False

    def increase_stock(self, product_id: int, amount: int) -> bool:
        try:
            self.product.update(
                stock=Products.stock + amount
            ).where(Products.product_id == product_id).execute()
            return True
        except Exception as e:
            logger.error(f"增加库存失败: {str(e)}")
            return False
