"""
Test script for MCP Web Search Server
This script tests the MCP server with sample input topics
"""

import asyncio
import json
import sys
import logging
from fastmcp import Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_mcp_server(topic: str):
    """
    Test the MCP server with a given topic
    
    Args:
        topic: The search topic to test
    """
    logger.info(f"Testing MCP server with topic: {topic}")
    
    # Create MCP client and use it within an async context manager
    # Use the correct SSE endpoint URL with port 8001
    async with Client("http://localhost:8001/sse") as client:
        try:
            # Call the search_web tool
            logger.info("Calling search_web tool...")
            response = await client.call_tool("search_web", {"topic": topic})
            
            # Convert the response to a dictionary
            response_dict = {}
            for content in response:
                if hasattr(content, "text"):
                    try:
                        # Try to parse the text as JSON
                        response_dict = json.loads(content.text)
                        break
                    except json.JSONDecodeError:
                        logger.warning("Response is not valid JSON")
                        response_dict = {"text": content.text}
            
            # Print response
            logger.info("Response received:")
            print(json.dumps(response_dict, indent=2))
            
            # Check if response contains expected fields
            if "results" in response_dict:
                logger.info(f"Found {len(response_dict['results'])} search results")
                return True
            else:
                logger.error("Response does not contain 'results' field")
                return False
                
        except Exception as e:
            logger.error(f"Error during test: {str(e)}")
            return False

async def main():
    """Main test function"""
    # Test topics
    test_topics = [
        "artificial intelligence",
        "climate change",
        "quantum computing"
    ]
    
    # Start the tests
    results = []
    for topic in test_topics:
        success = await test_mcp_server(topic)
        results.append((topic, success))
        
        # Add a delay between tests
        await asyncio.sleep(1)
    
    # Print summary
    logger.info("Test Summary:")
    for topic, success in results:
        status = "PASSED" if success else "FAILED"
        logger.info(f"Topic '{topic}': {status}")

if __name__ == "__main__":
    asyncio.run(main())
