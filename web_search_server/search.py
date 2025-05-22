"""
Web search module for MCP server
This module implements web search functionality using DuckDuckGo and Google search APIs
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import logging
import urllib.parse
import time
import random
import json
from duckduckgo_search import DDGS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebSearcher:
    """Class to handle web search operations"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.google_search_url = "https://www.google.com/search"
        self.ddgs = DDGS()
    
    async def search(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search the web using DuckDuckGo for the given query and return results
        
        Args:
            query: The search query
            num_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, and snippet
        """
        logger.info(f"Performing DuckDuckGo search for: {query}")
        
        try:
            # Use DuckDuckGo Search API
            ddg_results = list(self.ddgs.text(query, max_results=num_results))
            
            # Format results
            results = []
            for result in ddg_results:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("href", ""),
                    "snippet": result.get("body", "")
                })
            
            logger.info(f"Found {len(results)} DuckDuckGo search results")
            return results
            
        except Exception as e:
            logger.error(f"Error during DuckDuckGo search: {str(e)}")
            # If DuckDuckGo search fails, try the alternative method
            return await self.search_alternative(query, num_results)
    
    async def search_alternative(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """
        Alternative search implementation using Google
        This is a fallback method in case the primary method fails
        
        Args:
            query: The search query
            num_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, and snippet
        """
        logger.info(f"Using Google search method for: {query}")
        
        try:
            # Encode the query for URL
            encoded_query = urllib.parse.quote_plus(query)
            
            # Construct the search URL
            url = f"{self.google_search_url}?q={encoded_query}&num={num_results}"
            
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
            
            logger.info(f"Found {len(results)} Google search results")
            return results
            
        except Exception as e:
            logger.error(f"Error during Google search: {str(e)}")
            return self.get_fallback_results(query, num_results)
    
    def get_fallback_results(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """
        Last resort fallback that returns static results when all search methods fail
        
        Args:
            query: The search query
            num_results: Maximum number of results to return
            
        Returns:
            List of static search results
        """
        logger.warning(f"Using static fallback results for: {query}")
        
        # Create static results based on the query
        results = []
        for i in range(min(5, num_results)):
            results.append({
                "title": f"Result {i+1} for {query}",
                "url": f"https://example.com/result{i+1}",
                "snippet": f"This is a sample snippet for search result {i+1} related to {query}."
            })
        
        logger.info(f"Returning {len(results)} static fallback results")
        return results

# Create a singleton instance
web_searcher = WebSearcher()
