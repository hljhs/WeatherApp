"""
News API Interface Module
Used to interact with New York Times API to get news data
"""
import requests
import os
from datetime import datetime

class NewsAPI:
    def __init__(self, api_key=None):
        """Initialize News API interface
        
        Args:
            api_key: New York Times API key, if None tries to get from environment variables
        """
        self.api_key = api_key or os.environ.get('NYT_API_KEY') or "qn9lfPgRwicJ67dRV4es4JRgD2jGuVDq"
        if not self.api_key:
            print("Warning: New York Times API key not set, please set NYT_API_KEY environment variable or provide during initialization")
        
        self.base_url = "https://api.nytimes.com/svc"
    
    def search_articles(self, query, begin_date=None, end_date=None, sort="newest", page=0):
        """Search for articles related to the specified query
        
        Args:
            query: Search keyword
            begin_date: Start date (YYYYMMDD format)
            end_date: End date (YYYYMMDD format)
            sort: Sort method (newest, oldest, relevance)
            page: Page number
            
        Returns:
            dict: Dictionary containing article information, returns None if failed
        """
        if not self.api_key:
            return None
            
        endpoint = f"{self.base_url}/search/v2/articlesearch.json"
        params = {
            'q': query,
            'api-key': self.api_key,
            'page': page,
            'sort': sort
        }
        
        if begin_date:
            params['begin_date'] = begin_date
        if end_date:
            params['end_date'] = end_date
        
        try:
            response = requests.get(endpoint, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get news data: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error when requesting News API: {e}")
            return None
    
    def get_location_news(self, location, limit=5):
        """Get news related to specified location
        
        Args:
            location: Location name
            limit: Number of news items to return
            
        Returns:
            list: List containing news information, returns empty list if failed
        """
        result = self.search_articles(location)
        if not result or 'response' not in result or 'docs' not in result['response']:
            return []
        
        articles = result['response']['docs'][:limit]
        formatted_articles = []
        
        for article in articles:
            formatted_article = {
                'title': article.get('headline', {}).get('main', 'Unknown Title'),
                'abstract': article.get('abstract', 'No abstract'),
                'url': article.get('web_url', ''),
                'source': article.get('source', 'New York Times'),
                'published_date': article.get('pub_date', ''),
                'section': article.get('section_name', 'Uncategorized')
            }
            formatted_articles.append(formatted_article)
        
        return formatted_articles
