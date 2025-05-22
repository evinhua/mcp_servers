"""
Validation script for MCP Web Search Server
This script validates the search results and server response
"""

import asyncio
import json
import sys
import logging
from fastmcp import Client
import re
import urllib.parse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validation criteria
VALIDATION_CRITERIA = {
    "min_results": 3,  # Minimum number of results expected
    "min_title_length": 5,  # Minimum title length
    "min_snippet_length": 10,  # Minimum snippet length
    "required_fields": ["title", "url", "snippet"]  # Required fields in each result
}

async def validate_search_results(topic: str):
    """
    Validate the search results for a given topic
    
    Args:
        topic: The search topic to validate
    
    Returns:
        Tuple of (success, validation_report)
    """
    logger.info(f"Validating search results for topic: {topic}")
    
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
            
            # Initialize validation report
            validation_report = {
                "topic": topic,
                "success": False,
                "errors": [],
                "warnings": [],
                "result_count": 0,
                "valid_results": 0,
                "response_time": "N/A"  # Would track response time in a real implementation
            }
            
            # Check if response contains expected fields
            if "results" not in response_dict:
                validation_report["errors"].append("Response does not contain 'results' field")
                return False, validation_report
            
            # Check number of results
            results = response_dict["results"]
            validation_report["result_count"] = len(results)
            
            if len(results) < VALIDATION_CRITERIA["min_results"]:
                validation_report["warnings"].append(
                    f"Found only {len(results)} results, expected at least {VALIDATION_CRITERIA['min_results']}"
                )
            
            # Validate each result
            valid_results = 0
            for i, result in enumerate(results):
                result_valid = True
                result_errors = []
                
                # Check required fields
                for field in VALIDATION_CRITERIA["required_fields"]:
                    if field not in result:
                        result_errors.append(f"Missing required field: {field}")
                        result_valid = False
                        continue
                    
                    # Check field values
                    if field == "title" and len(result[field]) < VALIDATION_CRITERIA["min_title_length"]:
                        result_errors.append(f"Title too short: {len(result[field])} chars")
                        result_valid = False
                    
                    if field == "snippet" and len(result[field]) < VALIDATION_CRITERIA["min_snippet_length"]:
                        result_errors.append(f"Snippet too short: {len(result[field])} chars")
                        result_valid = False
                    
                    if field == "url" and not result[field].startswith(("http://", "https://")):
                        result_errors.append(f"Invalid URL format: {result[field]}")
                        result_valid = False
                
                # Check if URL is related to topic
                if "url" in result and "topic" in response_dict:
                    url_parts = urllib.parse.urlparse(result["url"]).netloc.lower()
                    topic_words = topic.lower().split()
                    
                    # Check if any topic word is in the URL (simple relevance check)
                    if not any(word in url_parts for word in topic_words if len(word) > 3):
                        validation_report["warnings"].append(
                            f"Result {i+1} URL may not be relevant to topic: {result['url']}"
                        )
                
                if result_valid:
                    valid_results += 1
                else:
                    validation_report["errors"].extend([f"Result {i+1}: {err}" for err in result_errors])
            
            validation_report["valid_results"] = valid_results
            
            # Determine overall success
            validation_report["success"] = (
                len(validation_report["errors"]) == 0 and 
                validation_report["valid_results"] >= VALIDATION_CRITERIA["min_results"]
            )
            
            return validation_report["success"], validation_report
                
        except Exception as e:
            logger.error(f"Error during validation: {str(e)}")
            return False, {
                "topic": topic,
                "success": False,
                "errors": [f"Exception during validation: {str(e)}"],
                "warnings": [],
                "result_count": 0,
                "valid_results": 0
            }

async def main():
    """Main validation function"""
    # Validation topics - using diverse topics to test robustness
    validation_topics = [
        "renewable energy",
        "machine learning applications",
        "space exploration",
        "sustainable agriculture",
        "cybersecurity best practices"
    ]
    
    # Start the validation
    results = []
    for topic in validation_topics:
        success, report = await validate_search_results(topic)
        results.append(report)
        
        # Add a delay between validations
        await asyncio.sleep(2)
    
    # Print summary
    logger.info("Validation Summary:")
    for report in results:
        status = "PASSED" if report["success"] else "FAILED"
        logger.info(f"Topic '{report['topic']}': {status} - {report['valid_results']}/{report['result_count']} valid results")
        
        if report["errors"]:
            logger.info(f"  Errors: {len(report['errors'])}")
            for error in report["errors"][:3]:  # Show first 3 errors
                logger.info(f"    - {error}")
            
        if report["warnings"]:
            logger.info(f"  Warnings: {len(report['warnings'])}")
            for warning in report["warnings"][:3]:  # Show first 3 warnings
                logger.info(f"    - {warning}")
    
    # Save validation report
    with open("validation_report.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info("Validation report saved to validation_report.json")

if __name__ == "__main__":
    asyncio.run(main())
