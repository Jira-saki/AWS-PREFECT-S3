"""
Unit tests for data transformation
"""

import pytest
import pandas as pd
from datetime import datetime
from src.transform import DataTransformer


@pytest.fixture
def sample_api_response():
    """Sample GitHub API response for testing"""
    return {
        "total_count": 2,
        "items": [
            {
                "id": 123,
                "name": "test-repo",
                "full_name": "user/test-repo",
                "owner": {"login": "user", "id": 456},
                "description": "Test repository",
                "stargazers_count": 100,
                "forks_count": 10,
                "language": "Python",
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-02T00:00:00Z",
                "html_url": "https://github.com/user/test-repo",
            },
            {
                "id": 789,
                "name": "another-repo",
                "full_name": "dev/another-repo",
                "owner": {"login": "dev", "id": 101},
                "description": None,  # Test missing description
                "stargazers_count": 50,
                "forks_count": 5,
                "language": None,  # Test missing language
                "created_at": "2024-02-01T00:00:00Z",
                "updated_at": "2024-02-02T00:00:00Z",
                "html_url": "https://github.com/dev/another-repo",
            },
        ],
    }


@pytest.fixture
def transformer():
    """DataTransformer instance"""
    return DataTransformer()


def test_flatten_repo_data(transformer, sample_api_response):
    """Test flattening nested JSON to DataFrame"""
    df = transformer.flatten_repo_data(sample_api_response)

    # Check DataFrame shape
    assert df.shape[0] == 2  # 2 repos
    assert df.shape[1] == 12  # 12 columns

    # Check columns exist
    expected_columns = [
        "repo_id",
        "repo_name",
        "full_name",
        "owner_login",
        "owner_id",
        "description",
        "stars",
        "forks",
        "language",
        "created_at",
        "updated_at",
        "url",
    ]
    assert list(df.columns) == expected_columns

    # Check data values
    assert df.iloc[0]["repo_id"] == 123
    assert df.iloc[0]["repo_name"] == "test-repo"
    assert df.iloc[0]["owner_login"] == "user"
    assert df.iloc[0]["stars"] == 100


def test_clean_data(transformer, sample_api_response):
    """Test data cleaning"""
    df = transformer.flatten_repo_data(sample_api_response)
    df_clean = transformer.clean_data(df)

    # Check datetime conversion
    assert pd.api.types.is_datetime64_any_dtype(df_clean["created_at"])
    assert pd.api.types.is_datetime64_any_dtype(df_clean["updated_at"])

    # Check missing values filled
    assert df_clean.iloc[1]["description"] == "No description"
    assert df_clean.iloc[1]["language"] == "Unknown"

    # Check extracted_at added
    assert "extracted_at" in df_clean.columns
    assert pd.api.types.is_datetime64_any_dtype(df_clean["extracted_at"])


def test_empty_response(transformer):
    """Test handling empty API response"""
    empty_response = {"total_count": 0, "items": []}
    df = transformer.flatten_repo_data(empty_response)

    assert df.shape[0] == 0  # No rows
    assert isinstance(df, pd.DataFrame)  # Returns DataFrame


def test_save_to_parquet(transformer, sample_api_response, tmp_path):
    """Test saving to Parquet format"""
    df = transformer.flatten_repo_data(sample_api_response)
    df_clean = transformer.clean_data(df)

    # Convert datetime to string (as in actual pipeline)
    df_clean["created_at"] = df_clean["created_at"].astype(str)
    df_clean["updated_at"] = df_clean["updated_at"].astype(str)
    df_clean["extracted_at"] = df_clean["extracted_at"].astype(str)

    # Save to temp file
    output_path = tmp_path / "test.parquet"
    transformer.save_to_parquet(df_clean, str(output_path))

    # Check file exists
    assert output_path.exists()

    # Read back and verify
    df_read = pd.read_parquet(output_path)
    assert df_read.shape == df_clean.shape
    assert list(df_read.columns) == list(df_clean.columns)
