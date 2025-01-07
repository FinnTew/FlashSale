import logging
import threading
import time

import redis

from conf.conf import conf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DistributedTokenBucket:
    """
    分布式令牌桶
    """

    # Lua脚本: 原子性获取令牌
    ACQUIRE_TOKEN_SCRIPT = """
    local bucket_key = KEYS[1]
    local tokens_key = KEYS[2]
    local timestamp_key = KEYS[3]
    local rate = tonumber(ARGV[1])
    local capacity = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local requested = tonumber(ARGV[4])
    
    -- 获取当前令牌数和上次更新时间
    local tokens = tonumber(redis.call('get', tokens_key) or capacity)
    local last_time = tonumber(redis.call('get', timestamp_key) or now)
    
    -- 计算需要补充的令牌
    local delta = math.max(0, now - last_time)
    local new_tokens = math.min(capacity, tokens + (delta * rate))
    
    -- 判断是否有足够的令牌
    if new_tokens >= requested then
        -- 扣除令牌并更新状态
        new_tokens = new_tokens - requested
        redis.call('set', tokens_key, new_tokens)
        redis.call('set', timestamp_key, now)
        return 1
    end
    
    return 0
    """

    def __init__(
            self,
            redis_host: str = conf.redis.host,
            redis_port: int = conf.redis.port,
            redis_db: int = conf.redis.db,
            rate: float = 10.0,  # 每秒补充的令牌数
            capacity: int = 100,  # 桶的容量
            namespace: str = 'default',  # 用于区分不同的限流器
            local_cache_time: float = 0.1  # 本地缓存时间，秒
    ):
        # Redis连接
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )

        self.rate = rate
        self.capacity = capacity
        self.namespace = namespace
        self.local_cache_time = local_cache_time

        # 用于本地缓存的变量
        self._local_tokens = capacity
        self._last_update_time = time.time()
        self._lock = threading.Lock()

        # 预编译Lua脚本
        self._acquire_token_script = self.redis_client.register_script(
            self.ACQUIRE_TOKEN_SCRIPT
        )

        # 初始化Redis中的令牌桶
        self._init_bucket()

    def _init_bucket(self):
        """初始化Redis中的令牌桶"""
        bucket_key = f"{self.namespace}:token_bucket"
        tokens_key = f"{bucket_key}:tokens"
        timestamp_key = f"{bucket_key}:timestamp"

        # 使用Redis的事务确保原子性初始化
        with self.redis_client.pipeline() as pipe:
            try:
                pipe.watch(tokens_key, timestamp_key)

                # 如果键不存在，则初始化
                if not self.redis_client.exists(tokens_key):
                    pipe.multi()
                    pipe.set(tokens_key, self.capacity)
                    pipe.set(timestamp_key, time.time())
                    pipe.execute()

            except Exception as e:
                logger.error(f"初始化令牌桶失败: {str(e)}")
                raise

    def acquire(self, tokens: int = 1, timeout: float = 0) -> bool:
        """
        尝试获取指定数量的令牌

        Args:
            tokens: 需要的令牌数量
            timeout: 等待超时时间，0表示不等待

        Returns:
            bool: 是否成功获取令牌
        """
        start_time = time.time()

        while True:
            # 先尝试从本地缓存获取
            if self._try_acquire_local(tokens):
                return True

            # 本地获取失败，尝试从Redis获取
            if self._try_acquire_redis(tokens):
                return True

            # 如果设置了超时且未超时，继续尝试
            if timeout > 0 and (time.time() - start_time) < timeout:
                time.sleep(0.01)  # 短暂休眠避免死循环
                continue

            return False

    def _try_acquire_local(self, tokens: int) -> bool:
        """尝试从本地缓存获取令牌"""
        with self._lock:
            now = time.time()
            # 检查是否需要刷新本地缓存
            if now - self._last_update_time >= self.local_cache_time:
                return False

            if self._local_tokens >= tokens:
                self._local_tokens -= tokens
                return True

            return False

    def _try_acquire_redis(self, tokens: int) -> bool:
        """从Redis获取令牌"""
        bucket_key = f"{self.namespace}:token_bucket"
        tokens_key = f"{bucket_key}:tokens"
        timestamp_key = f"{bucket_key}:timestamp"

        try:
            result = self._acquire_token_script(
                keys=[bucket_key, tokens_key, timestamp_key],
                args=[
                    self.rate,
                    self.capacity,
                    time.time(),
                    tokens
                ]
            )

            # 更新本地缓存
            if result == 1:
                with self._lock:
                    self._local_tokens = float(
                        self.redis_client.get(tokens_key) or self.capacity
                    )
                    self._last_update_time = time.time()
                return True

            return False

        except Exception as e:
            logger.error(f"Redis操作失败: {str(e)}")
            return False

    def get_token_count(self) -> float:
        """获取当前可用的令牌数"""
        tokens_key = f"{self.namespace}:token_bucket:tokens"
        try:
            return float(self.redis_client.get(tokens_key) or self.capacity)
        except Exception as e:
            logger.error(f"获取令牌数量失败: {str(e)}")
            return 0.0

class MultiLevelRateLimiter:
    """多级限流器"""

    def __init__(
            self,
            redis_host: str = conf.redis.host,
            redis_port: int = conf.redis.port,
            redis_db: int = conf.redis.db
    ):
        self.limiters = []
        self.redis_params = {
            'redis_host': redis_host,
            'redis_port': redis_port,
            'redis_db': redis_db
        }

    def add_limiter(
            self,
            rate: float,
            capacity: int,
            namespace: str
    ) -> None:
        """添加一个限流层级"""
        limiter = DistributedTokenBucket(
            rate=rate,
            capacity=capacity,
            namespace=namespace,
            **self.redis_params
        )
        self.limiters.append(limiter)

    def acquire(self, tokens: int = 1, timeout: float = 0) -> bool:
        """
        尝试通过所有限流层级
        只有所有层级都通过才算成功
        """
        start_time = time.time()

        for limiter in self.limiters:
            remaining_timeout = max(
                0,
                timeout - (time.time() - start_time)
            ) if timeout > 0 else 0

            if not limiter.acquire(tokens, remaining_timeout):
                return False

        return True

multi_limiter = MultiLevelRateLimiter()

for limiter in conf.limiters:
    multi_limiter.add_limiter(
        rate=limiter.rate,
        capacity=limiter.capacity,
        namespace=limiter.namespace
    )