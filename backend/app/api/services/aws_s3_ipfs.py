# app/services/aws_s3_ipfs.py
import boto3
import requests
import io
import uuid
import aiofiles # Recommended for async file handling
from botocore.exceptions import ClientError
from fastapi import UploadFile, HTTPException
from app.core.config import settings

# Initialize S3 client 
# NOTE: Using explicit keys from settings for development, but IAM role is better for production EC2.
s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

async def upload_and_pin_file(
    file: UploadFile, 
    uploader_id: int, 
    is_final_version: bool = False
) -> dict:
    """Uploads to S3 and pins to IPFS if is_final_version is True."""
    
    # 1. Determine Bucket and Key
    bucket_name = settings.S3_VERIFIED_BUCKET if is_final_version else settings.S3_RAW_BUCKET
    file_id = str(uuid.uuid4())
    s3_key = f"user-{uploader_id}/{file_id}-{file.filename}"

    # Read file content fully into memory (required for IPFS API and consistent S3 upload)
    file_content = await file.read()
    file_buffer = io.BytesIO(file_content)

    # 2. Upload to S3
    try:
        s3_client.upload_fileobj(
            file_buffer, 
            bucket_name, 
            s3_key, 
            ExtraArgs={'ContentType': file.content_type}
        )
    except ClientError as e:
        print(f"S3 Upload Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to store file on S3.")

    s3_url = f"s3://{bucket_name}/{s3_key}"
    ipfs_cid = None
    
    # 3. Pin to IPFS (Only for final/approved documents)
    if is_final_version:
        file_buffer.seek(0)
        files = {'file': (file.filename, file_buffer, file.content_type)}
        
        # Use a synchronous requests call (Blocking, but simpler than httpx)
        try:
            response = requests.post(f"{settings.IPFS_API_URL}/api/v0/add", files=files)
            response.raise_for_status()
            ipfs_cid = response.json()['Hash']
            
        except requests.exceptions.RequestException as e:
            print(f"IPFS API request failed: {e}")
            raise HTTPException(status_code=500, detail="Could not connect to IPFS node for pinning.")

    return {
        "s3_key": s3_key,
        "s3_bucket": bucket_name,
        "ipfs_cid": ipfs_cid,
        "original_file_url": s3_url
    }