from src.storage import S3Storage
from src.api_client import GitHubAPIClient
from src.config import GITHUB_TOKEN

# Test S3 connection
print("Testing S3 connection...")
storage = S3Storage()

if storage.test_connection():
    print("✅ S3 connection successful!\n")
    
    # Fetch some GitHub data
    print("Fetching GitHub data...")
    client = GitHubAPIClient(token=GITHUB_TOKEN)
    results = client.search_trending_repos(language="python", days_back=7, per_page=5)
    
    if results:
        print(f"✅ Fetched {len(results['items'])} repos\n")
        
        # Upload to S3
        print("Uploading to S3...")
        s3_key = storage.upload_json(results, prefix="raw")
        
        if s3_key:
            print(f"\n🎉 Success! Data saved to S3")
        else:
            print("\n❌ Upload failed")
    else:
        print("❌ Failed to fetch GitHub data")
else:
    print("❌ S3 connection failed")
