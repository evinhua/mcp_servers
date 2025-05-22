"""
MCP Server with Web Search Functionality
This server implements the Model Context Protocol (MCP) using FastMCP
and provides web search capabilities for input topics.
"""

import asyncio
from fastmcp import FastMCP
from fastapi import FastAPI
from typing import Dict, List, Any, Optional
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP
server = FastMCP("WebSearchServer")

# Import the web search module
from search import web_searcher

@server.tool()
async def search_web(topic: str, num_results: int = 10) -> Dict[str, Any]:
    """
    Search the web for the given topic and return results.
    
    Args:
        topic: The search topic
        num_results: Maximum number of results to return
        
    Returns:
        Dictionary with search results
    """
    logger.info(f"Searching for topic: {topic}")
    start_time = time.time()
    
    try:
        # Try the primary search method first
        results = await web_searcher.search(topic, num_results)
        
        # If primary method returns no results, try alternative method
        if not results:
            logger.warning(f"Primary search returned no results for '{topic}', trying alternative method")
            results = await web_searcher.search_alternative(topic, num_results)
        
        # Calculate search time
        search_time = time.time() - start_time
        
        return {
            "topic": topic,
            "results": results,
            "count": len(results),
            "search_time_seconds": round(search_time, 2)
        }
    except Exception as e:
        logger.error(f"Error in search_web: {str(e)}")
        return {
            "topic": topic,
            "error": str(e),
            "results": [],
            "count": 0,
            "search_time_seconds": round(time.time() - start_time, 2)
        }

@server.resource(uri="resource://search_info")
def search_info() -> Dict[str, Any]:
    """Provide information about the search service"""
    return {
        "name": "Web Search Service",
        "description": "Searches the web for information on various topics",
        "version": "1.1.0",
        "supported_search_engines": ["DuckDuckGo", "Google"],
        "max_results_per_query": 10,
        "features": [
            "Real-time web search",
            "Multiple search engines",
            "Fallback mechanisms",
            "Search time tracking"
        ]
    }

if __name__ == "__main__":
    # This section is for local testing only
    # In production, use uvicorn to run the app
    server.run(transport="sse", port=8001)
