"""MinIO S3-compatible object storage client."""

from io import BytesIO

from minio import Minio

from app.config import settings


class MinIOManager:
    """Manages MinIO connections for simulation files and reports."""

    def __init__(self):
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_USE_SSL,
        )
        self.bucket = settings.MINIO_BUCKET
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Create the bucket if it doesn't exist."""
        try:
            if not self.client.bucket_exists(self.bucket):
                self.client.make_bucket(self.bucket)
        except Exception:
            pass  # Will be created on first use in production

    def upload_file(self, object_name: str, data: bytes, content_type: str = "application/octet-stream") -> str:
        """Upload a file and return its URL."""
        self.client.put_object(
            self.bucket,
            object_name,
            BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        return f"/{self.bucket}/{object_name}"

    def upload_pdf(self, object_name: str, pdf_data: bytes) -> str:
        """Upload a PDF report."""
        return self.upload_file(object_name, pdf_data, "application/pdf")

    def get_file(self, object_name: str) -> bytes:
        """Download a file."""
        response = self.client.get_object(self.bucket, object_name)
        return response.read()

    def get_presigned_url(self, object_name: str, expires_hours: int = 24) -> str:
        """Generate a presigned URL for download."""
        from datetime import timedelta
        return self.client.presigned_get_object(
            self.bucket, object_name, expires=timedelta(hours=expires_hours)
        )


minio_manager = MinIOManager()
