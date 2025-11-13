"""
GitHub Trending Repos Data Pipeline
Orchestrated with Prefect
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from prefect import flow, task
from datetime import datetime
import pandas as pd
from typing import Dict, Any

from src.api_client import GitHubAPIClient
from src.storage import S3Storage
from src.transform import DataTransformer
from src.config import GITHUB_TOKEN


# Extract
@task(name="Fetch GitHub Data", retries=3, retry_delay_seconds=60)
def fetch_github_data(
    language: str = "python", days_back: int = 7, per_page: int = 100
) -> Dict[str, Any]:
    """
    Fetch trending repositories from GitHub API

    Args:
        language: Programming language to filter
        days_back: How many days back to search
        per_page: Number of results per page

    Returns:
        API response with repository data
    """
    # สร้าง GitHubAPIClient
    client = GitHubAPIClient(token=GITHUB_TOKEN)

    # เรียก search_trending_repos
    results = client.search_trending_repos(
        language=language, days_back=days_back, per_page=per_page
    )

    # log จำนวน repos ที่ได้
    print(f"✅ Fetched {len(results['items'])} repos")

    #  return results
    return results


# LOAD - Raw
@task(name="Save Raw Data to S3")
def save_raw_to_s3(data: Dict[str, Any]) -> str:
    """
    Save raw JSON data to S3

    Args:
        data: Raw API response

    Returns:
        S3 key where data was saved
    """
    #  สร้าง S3Storage
    storage = S3Storage()

    #  upload JSON ไป S3 raw layer
    s3_key = storage.upload_json(data, prefix="raw")

    # return s3_key
    return s3_key


# TRANSFORM
@task(name="Transform Data")
def transform_data(data: Dict[str, Any]) -> pd.DataFrame:
    """
    Transform raw data to structured format

    Args:
        data: Raw API response

    Returns:
        Cleaned DataFrame
    """
    #  สร้าง DataTransformer
    transformer = DataTransformer()

    # Flatten data
    df = transformer.flatten_repo_data(data)

    #  clean data
    df_clean = transformer.clean_data(df)

    # log shape
    print(f"✅ Transformed {df_clean.shape[0]} rows, {df_clean.shape[1]} columns")

    # TODO: return df_clean
    return df_clean


# LOAD - Processed
@task(name="Save Processed Data to S3")
def save_processed_to_s3(df: pd.DataFrame) -> str:
    """
    Save processed Parquet data to S3

    Args:
        df: Cleaned DataFrame

    Returns:
        S3 key where data was saved
    """
    #  แปลง datetime columns เป็น string (แก้ปัญหา Arrow)
    df_to_save = df.copy()
    df_to_save["created_at"] = df_to_save["created_at"].astype(str)
    df_to_save["updated_at"] = df_to_save["updated_at"].astype(str)
    df_to_save["extracted_at"] = df_to_save["extracted_at"].astype(str)

    # save เป็น parquet file ชั่วคราว
    import os

    os.makedirs("data", exist_ok=True)
    temp_path = "data/temp_processed.parquet"
    df_to_save.to_parquet(temp_path, compression="snappy", index=False)

    # อ่าน parquet file เป็น bytes
    with open(temp_path, "rb") as f:
        parquet_data = f.read()

    # สร้าง S3 key สำหรับ processed layer
    storage = S3Storage()
    now = datetime.now()
    s3_key = f"processed/year={now.year}/month={now.month:02d}/day={now.day:02d}/github_trending.parquet"

    # upload ไป S3
    storage.s3_client.put_object(
        Bucket=storage.bucket_name,
        Key=s3_key,
        Body=parquet_data,
        ContentType="application/octet-stream",
    )

    #  ลบ temp file
    os.remove(temp_path)

    #  log และ return s3_key
    print(f"✅ Uploaded to s3://{storage.bucket_name}/{s3_key}")
    return s3_key


@flow(name="GitHub Trending Repos Pipeline", log_prints=True)
def github_pipeline(language: str = "python", days_back: int = 7):
    """
    Main pipeline flow

    Args:
        language: Programming language to track
        days_back: How many days back to search
    """
    print(f"🚀 Starting pipeline for {language} repos (last {days_back} days)")

    # Task 1 - Fetch data
    raw_data = fetch_github_data(language=language, days_back=days_back)

    # Task 2 - Save raw to S3
    raw_s3_key = save_raw_to_s3(raw_data)

    #  Task 3 - Transform data
    df_clean = transform_data(raw_data)

    #  Task 4 - Save processed to S3
    processed_s3_key = save_processed_to_s3(df_clean)

    # Summary
    print(f"\n✅ Pipeline completed!")
    print(f"Raw data: {raw_s3_key}")
    print(f"Processed data: {processed_s3_key}")

    return {"raw_s3_key": raw_s3_key, "processed_s3_key": processed_s3_key}


if __name__ == "__main__":
    # Run the pipeline
    github_pipeline(language="python", days_back=7)
