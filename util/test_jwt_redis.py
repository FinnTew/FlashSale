import time
import unittest

from util.jwt_redis import JWTRedis


class TestJWTRedis(unittest.TestCase):
    def setUp(self):
        # 初始化JWTRedis实例
        self.jwt_redis = JWTRedis()

        # 测试用户ID
        self.test_user_id = "test_user_123"

        # 清理测试数据
        self.jwt_redis.invalidate_token(self.test_user_id)

    def test_generate_token(self):
        # 测试生成token
        token_info = self.jwt_redis.generate_token(
            user_id=self.test_user_id,
            expire_minutes=1,
            role="admin"
        )

        # 验证返回的token信息
        self.assertIn('token', token_info)
        self.assertIn('expire_time', token_info)

        # 验证token有效性
        payload = self.jwt_redis.verify_token(token_info['token'])
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], str(self.test_user_id))
        self.assertEqual(payload['role'], "admin")

    def test_token_caching(self):
        # 测试token缓存机制

        # 首次生成token
        first_token = self.jwt_redis.generate_token(
            user_id=self.test_user_id,
            expire_minutes=1
        )

        # 立即再次请求token
        second_token = self.jwt_redis.generate_token(
            user_id=self.test_user_id,
            expire_minutes=1
        )

        # 验证返回相同的token
        self.assertEqual(first_token['token'], second_token['token'])

    def test_token_expiration(self):
        # 测试token过期

        # 生成一个很快过期的token
        token_info = self.jwt_redis.generate_token(
            user_id=self.test_user_id,
            expire_minutes=1/60  # 1秒
        )

        # 等待token过期
        time.sleep(2)

        # 验证token已失效
        self.assertIsNone(self.jwt_redis.verify_token(token_info['token']))

        # 再次生成token应该得到新token
        new_token_info = self.jwt_redis.generate_token(
            user_id=self.test_user_id,
            expire_minutes=1
        )
        self.assertNotEqual(token_info['token'], new_token_info['token'])

    def test_invalidate_token(self):
        # 测试使token失效

        # 生成token
        token_info = self.jwt_redis.generate_token(
            user_id=self.test_user_id,
            expire_minutes=1
        )

        # 验证token有效
        self.assertIsNotNone(self.jwt_redis.verify_token(token_info['token']))

        # 使token失效
        self.assertTrue(self.jwt_redis.invalidate_token(self.test_user_id))

        # 验证token已失效
        self.assertIsNone(self.jwt_redis.verify_token(token_info['token']))

    def test_get_token(self):
        # 测试获取当前token

        # 初始状态应该没有token
        self.assertIsNone(self.jwt_redis.get_token(self.test_user_id))

        # 生成token
        original_token_info = self.jwt_redis.generate_token(
            user_id=self.test_user_id,
            expire_minutes=1
        )

        # 获取token并验证
        stored_token_info = self.jwt_redis.get_token(self.test_user_id)
        self.assertIsNotNone(stored_token_info)
        self.assertEqual(original_token_info['token'], stored_token_info['token'])

    def tearDown(self):
        # 清理测试数据
        self.jwt_redis.invalidate_token(self.test_user_id)

if __name__ == '__main__':
    unittest.main()