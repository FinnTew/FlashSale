import unittest
from unittest.mock import patch
from redis.exceptions import RedisError
from util.redis_util import RedisUtil

class TestRedisUtil(unittest.TestCase):

    @patch('redis.Redis')
    def setUp(self, MockRedis):
        """测试前的设置，创建 RedisUtil 实例。"""
        self.mock_redis = MockRedis.return_value
        self.redis_util = RedisUtil()

    def test_set(self):
        """测试设置键值对。"""
        self.mock_redis.set.return_value = True
        result = self.redis_util.set("key", "value")
        self.assertTrue(result)
        self.mock_redis.set.assert_called_once_with("key", "value", ex=None)

    def test_get(self):
        """测试获取键的值。"""
        self.mock_redis.get.return_value = b"value"
        result = self.redis_util.get("key")
        self.assertEqual(result, b"value")
        self.mock_redis.get.assert_called_once_with("key")

    def test_delete(self):
        """测试删除键。"""
        self.mock_redis.delete.return_value = 1
        result = self.redis_util.delete("key")
        self.assertEqual(result, 1)
        self.mock_redis.delete.assert_called_once_with("key")

    def test_exists(self):
        """测试检查键是否存在。"""
        self.mock_redis.exists.return_value = 1
        result = self.redis_util.exists("key")
        self.assertTrue(result)
        self.mock_redis.exists.assert_called_once_with("key")

    def test_hset(self):
        """测试在哈希中设置字段。"""
        self.mock_redis.hset.return_value = True
        result = self.redis_util.hset("hash", "field", "value")
        self.assertTrue(result)
        self.mock_redis.hset.assert_called_once_with("hash", "field", "value")

    def test_hget(self):
        """测试从哈希中获取字段。"""
        self.mock_redis.hget.return_value = b"value"
        result = self.redis_util.hget("hash", "field")
        self.assertEqual(result, b"value")
        self.mock_redis.hget.assert_called_once_with("hash", "field")

    def test_incr(self):
        """测试自增操作。"""
        self.mock_redis.incr.return_value = 10
        result = self.redis_util.incr("counter")
        self.assertEqual(result, 10)
        self.mock_redis.incr.assert_called_once_with("counter", 1)

    def test_decr(self):
        """测试自减操作。"""
        self.mock_redis.decr.return_value = 5
        result = self.redis_util.decr("counter")
        self.assertEqual(result, 5)
        self.mock_redis.decr.assert_called_once_with("counter", 1)

    def test_flushdb(self):
        """测试清空数据库。"""
        self.mock_redis.flushdb.return_value = True
        result = self.redis_util.flushdb()
        self.assertTrue(result)
        self.mock_redis.flushdb.assert_called_once()

    def test_set_multiple(self):
        """测试批量设置键值对。"""
        self.mock_redis.pipeline.return_value.__enter__.return_value = self.mock_redis
        self.redis_util.set_multiple({"key1": "value1", "key2": "value2"})
        self.mock_redis.set.assert_any_call("key1", "value1", ex=None)
        self.mock_redis.set.assert_any_call("key2", "value2", ex=None)

if __name__ == '__main__':
    unittest.main()