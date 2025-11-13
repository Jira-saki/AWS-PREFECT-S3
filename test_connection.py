from src.config import GITHUB_TOKEN
from src.api_client import GitHubAPIClient

client = GitHubAPIClient(token=GITHUB_TOKEN)

if client.test_connection():
    print("✅ Authentication successful!")
else:
    print("❌ Authentication failed")
