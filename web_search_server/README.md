"""
README for MCP Web Search Server

This server implements the Model Context Protocol (MCP) using FastMCP
and provides web search capabilities for input topics.
"""

# MCP Web Search Server

## Overview

This project implements a Model Context Protocol (MCP) server using FastMCP that performs web searches based on input topics. The server accepts requests with a topic field, searches the web for relevant information, and returns structured search results.

## Features

- MCP-compliant server using FastMCP
- Web search functionality with fallback mechanisms
- Robust error handling and logging
- Test and validation scripts

## Project Structure

- `main.py` - Main server implementation with MCP context provider
- `search.py` - Web search implementation using requests and BeautifulSoup
- `test_client.py` - Test script for the MCP server
- `validate.py` - Validation script for search results
- `todo.md` - Development task tracking

## Installation

1. Install required dependencies:
```
pip install fastmcp requests beautifulsoup4
```

2. Clone or download this repository

## Usage

### Starting the Server

Run the server with:

```
python main.py
```

Or for production:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Making Requests

You can make requests to the server using the FastMCP client:

```python
from fastmcp.client import MCPClient

async def search_topic(topic):
    client = MCPClient(base_url="http://localhost:8000")
    response = await client.request(data={"topic": topic})
    return response
```

### Response Format

The server returns responses in the following format:

```json
{
  "topic": "your search topic",
  "results": [
    {
      "title": "Result title",
      "url": "https://example.com/result",
      "snippet": "Brief description of the result"
    },
    ...
  ],
  "count": 10
}
```

## Testing

Run the test script to verify server functionality:

```
python test_client.py
```

## Validation

Validate search results with:

```
python validate.py
```

## Customization

You can customize the search behavior by modifying the `WebSearcher` class in `search.py`. The current implementation includes:

- Primary search method using Google
- Fallback search method for robustness

## License

This project is available under the MIT License.
