import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

def get_s3_client():
    import boto3
    r2_access_key = os.getenv("R2_ACCESS_KEY_ID")
    r2_secret_key = os.getenv("R2_SECRET_ACCESS_KEY")
    r2_endpoint = os.getenv("R2_ENDPOINT_URL")

    if not r2_access_key or not r2_secret_key:
        print("Не знайдено ключів доступу в .env")
        return None

    try:
        s3_client = boto3.client(
            's3',
            endpoint_url=r2_endpoint,
            aws_access_key_id=r2_access_key,
            aws_secret_access_key=r2_secret_key,
            region_name='auto'
        )
        return s3_client
    except Exception as e:
        print(f"Помилка створення клієнта boto3: {e}")
        return None


def upload_file_to_r2(file_content: bytes, s3_key: str, content_type: str = "image/jpeg") -> Optional[str]:
    r2_bucket = os.getenv("R2_BUCKET_NAME")

    s3 = get_s3_client()
    if s3 is None:
        return None

    try:
        s3.put_object(
            Bucket=r2_bucket,
            Key=s3_key,
            Body=file_content,
            ContentType=content_type
        )
        print(f"R2 Uploaded: {s3_key}")
        return s3_key
    except Exception as e:
        print(f"R2 Upload Failed for {s3_key}: {e}")
        return None