import pandas as pd
from typing import Dict, Any
from datetime import datetime


class DataTransformer:
    """Transform GitHub API data to structured format"""

    def flatten_repo_data(self, api_response: Dict[str, Any]) -> pd.DataFrame:
        """
        Flatten nested GitHub API response to DataFrame

        Args:
            api_response: Raw API response from GitHub

        Returns:
            Flattened pandas DataFrame
        """
        # Extract items from API response
        items = api_response.get("items", [])

        # TODO: Create list to store flattened records
        records = []

        # Loop through each repo in items
        for repo in items:
            # Extract fields we need
            record = {
                "repo_id": repo.get("id"),
                "repo_name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "owner_login": repo.get("owner", {}).get("login"),
                "owner_id": repo.get("owner", {}).get("id"),
                "description": repo.get("description"),
                "stars": repo.get("stargazers_count"),
                "forks": repo.get("forks_count"),
                "language": repo.get("language"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "url": repo.get("html_url"),
            }
            records.append(record)

        # Convert to DataFrame
        df = pd.DataFrame(records)

        # Return DataFrame
        return df

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and process DataFrame

        Args:
            df: Raw DataFrame

        Returns:
            Cleaned DataFrame
        """
        # Convert datetime strings to datetime objects
        df["created_at"] = pd.to_datetime(df["created_at"])
        df["updated_at"] = pd.to_datetime(df["updated_at"])

        # Fill missing language values with 'Unknown'
        # Fill missing description values with 'No description'
        df["description"] = df["description"].fillna("No description")
        df["language"] = df["language"].fillna("Unknown")

        #  Add extraction timestamp
        df["extracted_at"] = datetime.now()

        # Return cleaned DataFrame
        return df

    def save_to_parquet(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Save DataFrame to Parquet format

        Args:
            df: DataFrame to save
            output_path: Local file path to save
        """
        # Save as parquet with compression
        df.to_parquet(output_path, compression="snappy", index=False)
        print(f"✅ Saved to {output_path}")
