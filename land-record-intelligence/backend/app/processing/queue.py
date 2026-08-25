import json
from app.db.redis_client import redis_client
from app.core.logging import logger

class ProcessingQueue:
    QUEUE_NAME = "bhulekh:processing_jobs"

    @classmethod
    async def enqueue_job(cls, job_id: str) -> bool:
        """
        Pushes a job onto the processing queue.
        """
        try:
            if not redis_client.redis:
                logger.error("Redis client is not connected.")
                return False
                
            payload = json.dumps({"job_id": str(job_id)})
            await redis_client.redis.lpush(cls.QUEUE_NAME, payload)
            logger.info(f"Enqueued job: {job_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to enqueue job {job_id}: {e}")
            return False

    @classmethod
    async def dequeue_job(cls, timeout: int = 5) -> str | None:
        """
        Pops a job from the processing queue, waiting up to `timeout` seconds.
        Returns the job_id if found, else None.
        """
        try:
            if not redis_client.redis:
                return None
                
            result = await redis_client.redis.brpop(cls.QUEUE_NAME, timeout=timeout)
            if result:
                _, payload_str = result
                payload = json.loads(payload_str)
                return payload.get("job_id")
            return None
        except Exception as e:
            logger.error(f"Failed to dequeue job: {e}")
            return None
