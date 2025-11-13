from src.config import GITHUB_TOKEN
from src.api_client import GitHubAPIClient
import json 

# Initialize client
client = GitHubAPIClient(token=GITHUB_TOKEN)

# Search for trending Python repos from last 7 days
print("Fetching trending Python repositories...")
results = client.search_trending_repos(
    language="python",
    days_back=7,
    sort="stars",
    per_page=5  # Just get 5 for testing
)

if results:
    print(f"\nTotal results: {results['total_count']}")
    print(f"\nTop 5 trending Python repos:\n")
    
    for i, repo in enumerate(results['items'], 1):
        print(f"{i}. {repo['full_name']}")
        print(f"   ⭐ Stars: {repo['stargazers_count']}")
        print(f"   📝 Description: {repo['description']}")
        print(f"   🔗 URL: {repo['html_url']}\n")
else:
    print("Failed to fetch results")
