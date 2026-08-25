import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import logger

class RedisClient:
    def __init__(self):
        self.redis = None

    async def connect(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
        try:
            await self.redis.ping()
            logger.info("Connected to Redis successfully.")
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            raise

    async def close(self):
        if self.redis:
            await self.redis.close()

    async def ping(self) -> bool:
        try:
            if not self.redis:
                return False
            return await self.redis.ping()
        except Exception:
            return False

redis_client = RedisClient()
