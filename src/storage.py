import boto3
import json
from datetime import datetime
from typing import Dict, Any, Optional
from src.config import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, S3_BUCKET_NAME

class S3Storage:
    """Handle S3 storage operations"""
    
    def __init__(self):
        """Initialize S3 client"""
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
        )
        self.bucket_name = S3_BUCKET_NAME
    
    def upload_json(self, data: Dict[str, Any], prefix: str = "raw") -> Optional[str]:
        """
        Upload JSON data to S3 with date-based partitioning
        
        Args:
            data: Dictionary to upload as JSON
            prefix: Folder prefix (e.g., 'raw', 'processed')
        
        Returns:
            S3 key (path) if successful, None otherwise
        """
        try:
            # Generate timestamp
            now = datetime.now()
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            
            # Create date partitions
            year = now.strftime("%Y")
            month = now.strftime("%m")
            day = now.strftime("%d")
            
            # Build S3 key with partitioning
            s3_key = f"{prefix}/year={year}/month={month}/day={day}/github_trending_{timestamp}.json"
            
            # Convert data to JSON string
            json_data = json.dumps(data, indent=2)
            
            # Upload to S3
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json_data,
                ContentType='application/json'
            )
            
            print(f"✅ Uploaded to s3://{self.bucket_name}/{s3_key}")
            return s3_key
            
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test if S3 bucket is accessible"""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            return True
        except Exception as e:
            print(f"S3 connection error: {e}")
            return False