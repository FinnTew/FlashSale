import hashlib

from peewee import Model

from model.order_model import Orders0, Orders1, Orders2, Orders3

INDEX_MAP = {
    0: Orders0(),
    1: Orders1(),
    2: Orders2(),
    3: Orders3(),
}

class HashPartitioning:
    def __init__(self, num_tables: int):
        self.num_tables = num_tables

    def _generate_order_index(self, user_id: int, product_id: int, sale_id: int) -> int:
        order_str = f"order:{user_id}:{product_id}:{sale_id}"
        hash_obj = hashlib.sha256(order_str.encode())
        hash_hex = hash_obj.hexdigest()
        return int(hash_hex, 16) % self.num_tables

    def get_table_name(self, user_id: int, product_id: int, sale_id: int) -> Model:
        table_index = self._generate_order_index(user_id, product_id, sale_id)
        return f"orders_{table_index}"