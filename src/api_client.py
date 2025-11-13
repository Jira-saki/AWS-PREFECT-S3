# GitHub API client
import requests
from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class GitHubAPIClient:
    """Client for interacting with GitHub API"""

    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        """
        Initialize the GitHub API client

        Args:
            token: GitHub Personal Access Token
            base_url: GitHub API base URL
        """
        self.token = token  # Use parameter passed in
        self.base_url = base_url
        # Create a requests.Session() for connection pooling
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "python-github-client",  # GitHub requires this
            }
        )

    def _get_headers(self) -> Dict[str, str]:
        """
        Build request headers with authentication

        Returns:
            Dictionary of headers
        """
        # TODO: Return headers dict with:
        # - Authorization: token YOUR_TOKEN
        # - Accept: application/vnd.github.v3+json
        # - User-Agent: your-app-name

    def test_connection(self) -> bool:
        """
        Test if authentication works

        Returns:
            True if authenticated, False otherwise
        """
        try:
            response = self.session.get(f"{self.base_url}/user")
            return response.status_code == 200
        except Exception as e:
            print(f"Error: {e}")
            return False

    def search_trending_repos(
        self,
        language: str = "python",
        days_back: int = 7,
        sort: str = "stars",
        per_page: int = 100,
    ) -> Optional[Dict[str, Any]]:
        """
        Search for trending repositories

        Args:
            language: Programming language to filter
            days_back: How many days back to search
            sort: Sort by 'stars', 'forks', or 'updated'
            per_page: Results per page (max 100)

        Returns:
            Dictionary with search results or None if error
        """
        date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
        query = f"language:{language} created:>{date}"
        params = {"q": query, "sort": sort, "order": "desc", "per_page": per_page}
        response = self.session.get(
            f"{self.base_url}/search/repositories", params=params
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
