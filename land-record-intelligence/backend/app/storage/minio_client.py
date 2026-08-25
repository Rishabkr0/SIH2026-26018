import io
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

    def ensure_bucket_exists(self):
        try:
            if not self.client.bucket_exists(settings.MINIO_BUCKET):
                self.client.make_bucket(settings.MINIO_BUCKET)
        except Exception as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            raise

    def upload_object(self, object_name: str, data: bytes, length: int, content_type: str):
        self.ensure_bucket_exists()
        self.client.put_object(
            bucket_name=settings.MINIO_BUCKET,
            object_name=object_name,
            data=io.BytesIO(data),
            length=length,
            content_type=content_type
        )

    def delete_object(self, object_name: str):
        try:
            self.client.remove_object(settings.MINIO_BUCKET, object_name)
        except Exception as e:
            logger.error(f"Failed to delete minio object {object_name}: {e}")

    def get_object(self, object_name: str):
        return self.client.get_object(settings.MINIO_BUCKET, object_name)

minio_client = MinioClient()
