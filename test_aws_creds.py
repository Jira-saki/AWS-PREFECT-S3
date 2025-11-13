import boto3
from src.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME

print(f"Bucket: {S3_BUCKET_NAME}")
print(f"Region: {AWS_REGION}")
print(f"Access Key: {AWS_ACCESS_KEY_ID[:10]}..." if AWS_ACCESS_KEY_ID else "Missing!")

# Try listing buckets
try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    response = s3.list_buckets()
    print("\nYour S3 buckets:")
    for bucket in response['Buckets']:
        print(f"  - {bucket['Name']}")
        
except Exception as e:
    print(f"Error: {e}")
