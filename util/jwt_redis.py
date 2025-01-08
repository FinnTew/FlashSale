import jwt
import redis
import json
from typing import Dict, Optional, Union
from datetime import datetime, timedelta
from conf.conf import conf

class JWTRedis:
    def __init__(
            self,
            redis_host: str = conf.redis.host,
            redis_port: int = conf.redis.port,
            redis_password: str = conf.redis.password,
            redis_db: int = conf.redis.db,
            secret_key: str = 'finntew',
            algorithm: str = 'HS256',
            token_prefix: str = 'token:'
    ):
        """
        初始化JWT Redis工具类

        Args:
            redis_host: Redis服务器地址
            redis_port: Redis端口
            redis_password: Redis密码
            redis_db: Redis数据库编号
            secret_key: JWT密钥
            algorithm: JWT算法,默认HS256
            token_prefix: Redis中token键的前缀
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            password=redis_password,
            db=redis_db,
            decode_responses=True
        )
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_prefix = token_prefix

    def _get_redis_key(self, user_id: Union[str, int]) -> str:
        """生成Redis存储的key"""
        return f"{self.token_prefix}{user_id}"

    def generate_token(
            self,
            user_id: Union[str, int],
            expire_minutes: int = 30,
            **extra_payload
    ) -> Dict:
        """
        生成JWT Token,如果Redis中存在未过期token则直接返回

        Args:
            user_id: 用户ID
            expire_minutes: token过期时间(分钟)
            extra_payload: 额外的payload数据

        Returns:
            Dict: 包含token和过期时间的字典
        """
        redis_key = self._get_redis_key(user_id)

        # 检查Redis中是否存在未过期的token
        stored_data = self.redis_client.get(redis_key)
        if stored_data:
            try:
                stored_token_info = json.loads(stored_data)
                token = stored_token_info.get('token')
                # 验证token是否有效
                payload = jwt.decode(
                    token,
                    self.secret_key,
                    algorithms=[self.algorithm]
                )
                # token未过期,直接返回
                return stored_token_info
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                # token已过期或无效,删除Redis中的数据
                self.redis_client.delete(redis_key)

        # 生成新token
        now = datetime.utcnow()
        expire_time = now + timedelta(minutes=expire_minutes)

        payload = {
            'user_id': str(user_id),
            'exp': expire_time,
            'iat': now,
            **extra_payload
        }

        token = jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

        # 存储到Redis
        token_info = {
            'token': token,
            'expire_time': expire_time.timestamp()
        }
        self.redis_client.setex(
            redis_key,
            timedelta(minutes=expire_minutes),
            json.dumps(token_info)
        )

        return token_info

    def verify_token(self, token: str) -> Optional[Dict]:
        """
        验证token

        Args:
            token: JWT token

        Returns:
            Dict: token的payload
            None: token无效时返回None
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            # 验证Redis中是否存在该token
            user_id = payload.get('user_id')
            if user_id:
                redis_key = self._get_redis_key(user_id)
                stored_data = self.redis_client.get(redis_key)
                if stored_data:
                    stored_token_info = json.loads(stored_data)
                    if stored_token_info.get('token') == token:
                        return payload
            return None

        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    def invalidate_token(self, user_id: Union[str, int]) -> bool:
        """
        使token失效

        Args:
            user_id: 用户ID

        Returns:
            bool: 操作是否成功
        """
        redis_key = self._get_redis_key(user_id)
        return bool(self.redis_client.delete(redis_key))

    def get_token(self, user_id: Union[str, int]) -> Optional[Dict]:
        """
        获取用户当前token信息

        Args:
            user_id: 用户ID

        Returns:
            Dict: token信息
            None: 不存在或已过期
        """
        redis_key = self._get_redis_key(user_id)
        stored_data = self.redis_client.get(redis_key)

        if stored_data:
            try:
                token_info = json.loads(stored_data)
                token = token_info.get('token')
                # 验证token
                if self.verify_token(token):
                    return token_info
            except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
                self.redis_client.delete(redis_key)
        return None