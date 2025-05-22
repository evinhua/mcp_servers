"""
Web search module for MCP server
This module implements web search functionality using requests and BeautifulSoup
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import logging
import urllib.parse
import time
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearcher:
    """Class to handle web search operations"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.search_url = "https://www.google.com/search"
    
    async def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search the web for the given query and return results
        
        Args:
            query: The search query
            num_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, and snippet
        """
        logger.info(f"Performing web search for: {query}")
        
        # Encode the query for URL
        encoded_query = urllib.parse.quote_plus(query)
        
        # Construct the search URL
        url = f"{self.search_url}?q={encoded_query}&num={num_results}"
        
        try:
            # Make the request
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract search results
            results = []
            search_divs = soup.find_all('div', class_='g')
            
            for div in search_divs:
                if len(results) >= num_results:
                    break
                
                # Extract title and URL
                title_element = div.find('h3')
                if not title_element:
                    continue
                
                title = title_element.get_text()
                
                # Find the URL
                url_element = div.find('a')
                if not url_element or not url_element.get('href'):
                    continue
                
                url = url_element['href']
                if url.startswith('/url?q='):
                    url = url.split('/url?q=')[1].split('&')[0]
                
                # Extract snippet
                snippet_element = div.find('div', class_='VwiC3b')
                snippet = snippet_element.get_text() if snippet_element else ""
                
                # Add to results
                results.append({
                    "title": title,
                    "url": url,
                    "snippet": snippet
                })
                
                # Add a small delay to avoid rate limiting
                time.sleep(random.uniform(0.1, 0.3))
            
            logger.info(f"Found {len(results)} search results")
            return results
            
        except Exception as e:
            logger.error(f"Error during web search: {str(e)}")
            return []
    
    async def search_alternative(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Alternative search implementation using a different approach
        This is a fallback method in case the primary method fails
        
        Args:
            query: The search query
            num_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, and snippet
        """
        logger.info(f"Using alternative search method for: {query}")
        
        # Simulate search results for demonstration
        # In a real implementation, this would use a different search API or approach
        try:
            # Make a request to a different search engine or API
            # For demonstration, we'll create mock results
            results = []
            for i in range(min(5, num_results)):
                results.append({
                    "title": f"Result {i+1} for {query}",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"This is a sample snippet for search result {i+1} related to {query}."
                })
            
            logger.info(f"Found {len(results)} alternative search results")
            return results
            
        except Exception as e:
            logger.error(f"Error during alternative search: {str(e)}")
            return []

# Create a singleton instance
web_searcher = WebSearcher()
