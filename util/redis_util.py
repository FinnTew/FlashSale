import redis
from redis.exceptions import RedisError
from typing import Optional, Union, List, Dict
from conf.conf import conf

class RedisUtil:
    def __init__(self,
                 host: str = conf.redis.host,
                 port: int = conf.redis.port,
                 db: int = conf.redis.db,
                 password: str = conf.redis.password) -> None:
        """初始化 Redis 连接，测试连接是否成功。"""
        try:
            self.client = redis.Redis(host=host, port=port, db=db, password=password)
            self.client.ping()  # 测试连接
        except RedisError as error:
            raise ConnectionError(f"无法连接到 Redis 服务器: {error}")

    def set(self, key: str, value: Union[str, bytes], expire: Optional[int] = None) -> bool:
        """在 Redis 中设置一个键值对，可选设置过期时间。"""
        try:
            return self.client.set(key, value, ex=expire)
        except RedisError as error:
            print(f"设置键 {key} 时发生错误: {error}")
            return False

    def get(self, key: str) -> Optional[Union[str, bytes]]:
        """从 Redis 中获取一个键的值。"""
        try:
            return self.client.get(key)
        except RedisError as error:
            print(f"获取键 {key} 时发生错误: {error}")
            return None

    def delete(self, key: str) -> int:
        """从 Redis 中删除一个键。"""
        try:
            return self.client.delete(key)
        except RedisError as error:
            print(f"删除键 {key} 时发生错误: {error}")
            return 0

    def exists(self, key: str) -> bool:
        """检查一个键是否存在于 Redis 中。"""
        try:
            return self.client.exists(key) == 1
        except RedisError as error:
            print(f"检查键 {key} 是否存在时发生错误: {error}")
            return False

    def hset(self, name: str, key: str, value: Union[str, bytes]) -> bool:
        """在哈希中设置一个字段。"""
        try:
            return self.client.hset(name, key, value)
        except RedisError as error:
            print(f"在哈希 {name} 中设置字段 {key} 时发生错误: {error}")
            return False

    def hget(self, name: str, key: str) -> Optional[Union[str, bytes]]:
        """从哈希中获取一个字段的值。"""
        try:
            return self.client.hget(name, key)
        except RedisError as error:
            print(f"从哈希 {name} 中获取字段 {key} 时发生错误: {error}")
            return None

    def hgetall(self, name: str) -> Dict[str, Union[str, bytes]]:
        """获取哈希中的所有字段及其值。"""
        try:
            return self.client.hgetall(name)
        except RedisError as error:
            print(f"获取哈希 {name} 中所有字段时发生错误: {error}")
            return {}

    def lpush(self, name: str, *values: Union[str, bytes]) -> int:
        """将一个或多个值推送到列表的左侧。"""
        try:
            return self.client.lpush(name, *values)
        except RedisError as error:
            print(f"向列表 {name} 推送值时发生错误: {error}")
            return 0

    def lrange(self, name: str, start: int, end: int) -> List[Union[str, bytes]]:
        """获取列表中指定范围的元素。"""
        try:
            return self.client.lrange(name, start, end)
        except RedisError as error:
            print(f"从列表 {name} 获取范围时发生错误: {error}")
            return []

    def rpush(self, name: str, *values: Union[str, bytes]) -> int:
        """将一个或多个值推送到列表的右侧。"""
        try:
            return self.client.rpush(name, *values)
        except RedisError as error:
            print(f"向列表 {name} 推送值时发生错误: {error}")
            return 0

    def sadd(self, name: str, *values: Union[str, bytes]) -> int:
        """向集合中添加一个或多个成员。"""
        try:
            return self.client.sadd(name, *values)
        except RedisError as error:
            print(f"向集合 {name} 添加成员时发生错误: {error}")
            return 0

    def smembers(self, name: str) -> List[Union[str, bytes]]:
        """获取集合中的所有成员。"""
        try:
            return self.client.smembers(name)
        except RedisError as error:
            print(f"获取集合 {name} 中的成员时发生错误: {error}")
            return []

    def zadd(self, name: str, mapping: Dict[Union[str, bytes], float]) -> int:
        """向有序集合中添加一个或多个成员，或更新现有成员的分数。"""
        try:
            return self.client.zadd(name, mapping)
        except RedisError as error:
            print(f"向有序集合 {name} 添加成员时发生错误: {error}")
            return 0

    def zrange(self, name: str, start: int, end: int) -> List[Union[str, bytes]]:
        """按索引返回有序集合中的成员范围。"""
        try:
            return self.client.zrange(name, start, end)
        except RedisError as error:
            print(f"从有序集合 {name} 获取范围时发生错误: {error}")
            return []

    def flushdb(self) -> bool:
        """清空当前数据库。"""
        try:
            return self.client.flushdb()
        except RedisError as error:
            print(f"清空数据库时发生错误: {error}")
            return False

    def set_multiple(self, mapping: Dict[str, Union[str, bytes]], expire: Optional[int] = None) -> bool:
        """批量设置多个键值对，可以设置过期时间。"""
        try:
            with self.client.pipeline() as pipe:
                for key, value in mapping.items():
                    pipe.set(key, value, ex=expire)
                pipe.execute()
            return True
        except RedisError as error:
            print(f"批量设置键值对时发生错误: {error}")
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        """对键的值进行自增操作，默认增加 1。"""
        try:
            return self.client.incr(key, amount)
        except RedisError as error:
            print(f"自增键 {key} 时发生错误: {error}")
            return 0

    def decr(self, key: str, amount: int = 1) -> int:
        """对键的值进行自减操作，默认减少 1。"""
        try:
            return self.client.decr(key, amount)
        except RedisError as error:
            print(f"自减键 {key} 时发生错误: {error}")
            return 0

