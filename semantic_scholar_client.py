"""
Semantic Scholar API Client for fetching academic papers.

This module provides a clean interface to the Semantic Scholar API with
rate limiting, error handling, and structured data models.
"""

import time
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime

import requests


@dataclass
class Paper:
    """Structured representation of an academic paper."""
    paperId: str
    title: str
    authors: List[str]
    year: Optional[int]
    abstract: Optional[str]
    citationCount: Optional[int]
    url: Optional[str]
    
    def __post_init__(self):
        """Normalize author names to a consistent format."""
        if isinstance(self.authors, list):
            # Extract author names from author objects if needed
            self.authors = [
                author.get('name', author) if isinstance(author, dict) else str(author)
                for author in self.authors
            ]
        elif self.authors is None:
            self.authors = []


class SemanticScholarClient:
    """
    Client for interacting with the Semantic Scholar API.
    
    Features:
    - Keyword-based paper search
    - Rate limiting and throttling
    - Configurable fields and filters
    - Error handling
    """
    
    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
    
    DEFAULT_FIELDS = [
        "title",
        "authors",
        "year",
        "abstract",
        "citationCount",
        "url",
        "paperId"
    ]
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        requests_per_second: float = 5.0,
        timeout: int = 30
    ):
        """
        Initialize the Semantic Scholar client.
        
        Args:
            api_key: Optional API key for higher rate limits
            requests_per_second: Maximum requests per second (default: 5.0)
            timeout: Request timeout in seconds (default: 30)
        """
        self.api_key = api_key
        self.requests_per_second = requests_per_second
        self.timeout = timeout
        self.min_request_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
        
        # Setup session with headers
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"x-api-key": api_key})
    
    def _throttle(self) -> None:
        """Ensure we don't exceed the rate limit."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()
    
    def _make_request(
        self,
        params: dict
    ) -> dict:
        """
        Make an API request with throttling and error handling.
        
        Args:
            params: Query parameters for the API request
            
        Returns:
            JSON response as a dictionary
            
        Raises:
            requests.RequestException: For network or API errors
        """
        self._throttle()
        
        try:
            response = self.session.get(
                self.BASE_URL,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            raise requests.RequestException(
                f"Request timed out after {self.timeout} seconds"
            )
        except requests.exceptions.HTTPError as e:
            if response.status_code == 429:
                raise requests.RequestException(
                    "Rate limit exceeded. Please reduce request frequency."
                )
            elif response.status_code == 404:
                raise requests.RequestException("API endpoint not found.")
            else:
                raise requests.RequestException(
                    f"HTTP error {response.status_code}: {response.text}"
                )
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(f"Request failed: {str(e)}")
    
    def search_papers(
        self,
        query: str,
        limit: int = 100,
        fields: Optional[List[str]] = None,
        min_citations: Optional[int] = None,
        year_range: Optional[tuple] = None,
        offset: int = 0
    ) -> List[Paper]:
        """
        Search for papers by keyword query.
        
        Args:
            query: Search query (keywords)
            limit: Maximum number of results (default: 100, max: 1000)
            fields: List of fields to return (default: DEFAULT_FIELDS)
            min_citations: Minimum citation count filter
            year_range: Tuple of (min_year, max_year) for filtering
            offset: Number of results to skip (for pagination)
            
        Returns:
            List of Paper objects matching the query
        """
        if fields is None:
            fields = self.DEFAULT_FIELDS.copy()
        
        # Build query parameters
        params = {
            "query": query,
            "limit": min(limit, 1000),  # API max is 1000
            "offset": offset,
            "fields": ",".join(fields)
        }
        
        # Add filters if provided
        filters = []
        if min_citations is not None:
            filters.append(f"citationCount:>{min_citations}")
        if year_range is not None:
            min_year, max_year = year_range
            if min_year is not None:
                filters.append(f"year:>={min_year}")
            if max_year is not None:
                filters.append(f"year:<={max_year}")
        
        if filters:
            params["filter"] = ",".join(filters)
        
        try:
            response_data = self._make_request(params)
            papers = []
            
            for item in response_data.get("data", []):
                try:
                    # Extract authors list
                    authors = []
                    for author in item.get("authors", []):
                        if isinstance(author, dict):
                            authors.append(author.get("name", ""))
                        else:
                            authors.append(str(author))
                    
                    paper = Paper(
                        paperId=item.get("paperId", ""),
                        title=item.get("title", "No title"),
                        authors=authors,
                        year=item.get("year"),
                        abstract=item.get("abstract"),
                        citationCount=item.get("citationCount", 0),
                        url=item.get("url")
                    )
                    papers.append(paper)
                except Exception as e:
                    # Skip malformed papers but continue processing
                    print(f"Warning: Skipping paper due to parsing error: {e}")
                    continue
            
            return papers
            
        except requests.RequestException as e:
            print(f"Error searching papers: {e}")
            raise

