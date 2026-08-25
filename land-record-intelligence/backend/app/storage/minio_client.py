from minio import Minio
from app.core.config import settings
from app.core.logging import logger

class MinioClient:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=False # Local development
        )

    def verify_connection(self) -> bool:
        try:
            # Simple list_buckets to verify connection
            self.client.list_buckets()
            return True
        except Exception as e:
            logger.error(f"MinIO connection failed: {e}")
            return False

minio_client = MinioClient()
