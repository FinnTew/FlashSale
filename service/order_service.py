import logging
from datetime import datetime
import hashlib
import base64
import re
from model.base_model import db
from util.hash_partitioning import HashPartitioning

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class OrderService:
    def __init__(self):
        self.db = db
        self.partitioning = HashPartitioning(4)

    @staticmethod
    def _get_order_id(user_id: int, product_id: int, sale_id: int) -> str:
        order_str = f"order:{user_id}:{product_id}:{sale_id}"
        hash_obj = hashlib.sha256(order_str.encode())
        hash_base64 = (base64.urlsafe_b64encode(hash_obj.digest())
                       .decode()
                       .rstrip('='))
        order_pre = re.sub(r'[^a-zA-Z0-9]', '', hash_base64)
        now = datetime.now()
        timestamp_str = now.strftime('%Y%m%d%H%M%S') + f"{now.microsecond // 1000:03d}"
        return f"FS{order_pre[2:10]}-{timestamp_str}"

    def _execute_sql(self, query: str, params: tuple) -> bool:
        """通用 SQL 执行方法，处理异常"""
        try:
            self.db.execute_sql(query, params)
            return True
        except Exception as e:
            logging.error(f"SQL Error: {e}")
            return False

    def create_order(self, user_id: int, product_id: int, sale_id: int) -> bool:
        table_name = self.partitioning.get_table_name(user_id, product_id, sale_id)
        with self.db.atomic():
            # 加锁以避免并发插入相同订单
            exist_order = self.db.execute_sql(
                f'SELECT * FROM {table_name} WHERE user_id = ? AND product_id = ? AND sale_id = ? FOR UPDATE',
                (user_id, product_id, sale_id)
            ).fetchone()

            if exist_order is None:
                order_id = self._get_order_id(user_id, product_id, sale_id)
                insert_query = (
                    f'INSERT INTO {table_name} (order_id, user_id, product_id, sale_id, order_status) '
                    f'VALUES (?, ?, ?, ?, ?)'
                )
                return self._execute_sql(insert_query, (order_id, user_id, product_id, sale_id, 'PENDING'))
            else:
                logging.warning(f"Order already exists for user_id: {user_id}, product_id: {product_id}, sale_id: {sale_id}")
                return False

    def update_order_status(self, order_id: str, user_id: int, product_id, sale_id: int, new_status: str) -> bool:
        if new_status not in {'PENDING', 'COMPLETED', 'CANCELLED'}:
            logging.error("Invalid order status provided.")
            return False

        table_name = self.partitioning.get_table_name(user_id, product_id, sale_id)

        with self.db.atomic():
            # 加锁以确保数据一致性
            existing_order = self.db.execute_sql(
                f'SELECT * FROM {table_name} WHERE order_id = ? FOR UPDATE',
                (order_id,)
            ).fetchone()

            if existing_order:
                update_query = f'UPDATE {table_name} SET order_status = ? WHERE order_id = ?'
                return self._execute_sql(update_query, (new_status, order_id))
            else:
                logging.warning(f"Order not found for order_id: {order_id}")
                return False

    def get_order(self, order_id: str):
        order = {}
        for i in range(self.partitioning.num_tables):
            table_name = f"orders_{i}"
            order = self.db.execute_sql(f'SELECT * FROM {table_name} WHERE order_id = ?', (order_id,)).fetchone()
            if order is not None:
                break
        if order:
            return order
        else:
            logging.warning(f"Order not found for order_id: {order_id}")
            return None

    def get_all_orders(self):
        all_orders = []
        for i in range(self.partitioning.num_tables):
            table_name = f'orders_{i}'
            orders = self.db.execute_sql(f'SELECT * FROM {table_name}').fetchall()
            all_orders.extend(orders)
        return all_orders

    def delete_order(self, order_id: str) -> bool:
        for i in range(self.partitioning.num_tables):
            table_name  = f"orders_{i}"
            with self.db.atomic():
                # 加锁以确保删除操作的安全性
                existing_order = self.db.execute_sql(
                    f'SELECT * FROM {table_name} WHERE order_id = ? FOR UPDATE',
                    (order_id,)
                ).fetchone()

                if existing_order:
                    delete_query = f'DELETE FROM {table_name} WHERE order_id = ?'
                    return self._execute_sql(delete_query, (order_id,))
                else:
                    logging.warning(f"Order not found for order_id: {order_id}")
                    return False