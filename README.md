# MCP Servers

This repository contains Model Context Protocol (MCP) server implementations for various use cases.

## Projects

### Web Search Server

A FastMCP server that provides web search capabilities. The server accepts search topics and returns structured search results.

- Located in: `web_search_server/`
- Features:
  - Web search functionality with fallback mechanisms
  - Robust error handling and logging
  - Test and validation scripts

## Getting Started

1. Install required dependencies:
```
pip install fastmcp requests beautifulsoup4
```

2. Navigate to a specific server directory:
```
cd web_search_server
```

3. Run the server:
```
python main.py
```

## Testing

Each server includes its own test scripts. For example, to test the web search server:

```
cd web_search_server
python test_client.py
```

## Validation

To validate server functionality:

```
cd web_search_server
python validate.py
```

## License

This project is available under the MIT License.
