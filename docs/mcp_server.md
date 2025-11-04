# gpt4free MCP (Model Context Protocol) Server

The gpt4free MCP server provides an implementation of the Model Context Protocol standard, allowing AI assistants to access gpt4free capabilities through standardized interfaces.

## Overview

The MCP server exposes gpt4free capabilities through the Model Context Protocol standard, enabling AI assistants to utilize:

- Web search functionality
- Web scraping capabilities
- Image generation using various providers
- Text-to-audio conversion
- URL to markdown conversion (MarkItDown)
- Code generation

## Installation

To use the MCP server, you need to install gpt4free with the required dependencies:

```bash
pip install gpt4free
# or
uv pip install gpt4free
```

For full functionality, install with all dependencies:

```bash
pip install gpt4free[all]
# or
uv pip install gpt4free[all]
```

## Running the Server

### Using the CLI Command

The MCP server can be started using the built-in command:

```bash
g4f-mcp --http --port 8765
```

### Using the Script

Alternatively, you can use the provided script:

```bash
python scripts/start_mcp_server.py --port 8765
```

### Available Options

- `--http`: Run server in HTTP mode (default: True)
- `--host`: Host to bind the HTTP server to (default: 0.0.0)
- `--port`: Port to bind the HTTP server to (default: 8765)
- `--origin`: Origin URL for requests (optional)

## Endpoints

Once running, the server provides the following endpoints:

- **MCP endpoint**: `http://0.0.0.0:8765/mcp` - Main MCP JSON-RPC endpoint
- **Health check**: `http://0.0.0.0:8765/health` - Server health check

## Available Tools

### Web Search

- **Name**: `web_search`
- **Description**: Search the web for information using DuckDuckGo. Returns search results with titles, URLs, and snippets.
- **Parameters**:
  - `query` (required): The search query to execute
  - `max_results` (optional): Maximum number of results to return (default: 5)
  - `region` (optional): Search region (default: en-us)

### Web Scrape

- **Name**: `web_scrape`
- **Description**: Scrape and extract text content from a web page URL. Returns cleaned text content with optional word limit.
- **Parameters**:
  - `url` (required): The URL of the web page to scrape
 - `max_words` (optional): Maximum number of words to extract (default: 1000)

### Image Generation

- **Name**: `image_generation`
- **Description**: Generate images from text prompts using AI image generation providers. Returns a URL to the generated image.
- **Parameters**:
  - `prompt` (required): The text prompt describing the image to generate
  - `model` (optional): The image generation model to use (default: flux)
  - `width` (optional): Image width in pixels (default: 1024)
  - `height` (optional): Image height in pixels (default: 1024)

### Text-to-Audio

- **Name**: `text_to_audio`
- **Description**: Generate an audio URL from a text prompt using Pollinations AI text-to-speech service. Returns a direct URL to the generated audio file.
- **Parameters**:
  - `prompt` (required): The text prompt to the audio model (example: 'Read this: Hello, world!')
  - `voice` (optional): Voice option for text-to-speech (default: 'alloy')
  - `url_encode` (optional): Whether to URL-encode the prompt text (default: True)

### MarkItDown

- **Name**: `mark_it_down`
- **Description**: Convert a URL to markdown format using MarkItDown. Supports HTTP/HTTPS URLs and returns formatted markdown content.
- **Parameters**:
  - `url` (required): The URL to convert to markdown format (must be HTTP/HTTPS)
  - `max_content_length` (optional): Maximum content length for processing (default: 10000)

### Code Generation

- **Name**: `code_generation`
- **Description**: Generate code based on a text prompt using AI. Supports various programming languages and frameworks. Returns the generated code.
- **Parameters**:
  - `prompt` (required): The text prompt describing the code to generate
  - `model` (optional): The AI model to use for code generation (default: gpt-4o)
  - `language` (optional): The programming language for the generated code (default: python)
 - `max_tokens` (optional): Maximum number of tokens to generate (default: 2048)

### File Reading

- **Name**: `file_read`
- **Description**: Read the contents of a file from the filesystem. Returns the file content as text.
- **Parameters**:
  - `path` (required): The path to the file to read
  - `max_size` (optional): Maximum file size to read in bytes (default: 1048576 = 1MB)

### File Writing

- **Name**: `file_write`
- **Description**: Write content to a file in the filesystem. Creates or overwrites the file with the provided content.
- **Parameters**:
  - `path` (required): The path to the file to write
  - `content` (required): The content to write to the file
  - `overwrite` (optional): Whether to overwrite existing file (default: true)

### File Listing

- **Name**: `file_list`
- **Description**: List files and directories in a specified directory. Returns information about each item including type and size.
- **Parameters**:
  - `path` (required): The directory path to list
  - `recursive` (optional): Whether to list files recursively (default: false)
  - `max_items` (optional): Maximum number of items to return (default: 100)

### Code Execution

- **Name**: `code_execute`
- **Description**: Execute Python code snippets safely in a subprocess environment. Returns the output of the code execution.
- **Parameters**:
  - `code` (required): The Python code to execute
  - `timeout` (optional): Execution timeout in seconds (default: 10)

- **Name**: `code_execute_safe`
- **Description**: Execute Python code snippets in a restricted environment using AST analysis. Returns the output of the code execution.
- **Parameters**:
  - `code` (required): The Python code to execute in a restricted environment

### Database Operations
- **Name**: `database`
- **Description**: Execute SQL queries on SQLite databases. Supports SELECT, INSERT, UPDATE, DELETE statements. Returns query results or execution status.
- **Parameters**:
  - `db_path` (required): Path to the SQLite database file
  - `query` (required): SQL query to execute
 - `params` (optional): Parameters for the SQL query

### HTTP Requests
- **Name**: `http_request`
- **Description**: Send HTTP requests (GET, POST, PUT, DELETE) to external endpoints. Supports headers, query parameters, and request body. Returns response data.
- **Parameters**:
  - `url` (required): The URL to send the HTTP request to
  - `method` (optional): HTTP method to use (GET, POST, PUT, DELETE) (default: GET)
 - `headers` (optional): HTTP headers to include in the request
 - `params` (optional): Query parameters to include in the request
  - `body` (optional): Request body for POST/PUT requests
 - `timeout` (optional): Request timeout in seconds (default: 30)

## MCP Protocol Methods

The server supports the following MCP protocol methods:

- `initialize`: Initialize the MCP session
- `tools/list`: List all available tools
- `tools/call`: Call a specific tool with parameters
- `ping`: Health check method

## Example Usage

Here's an example of how to call the web search tool using curl:

```bash
curl -X POST http://0.0.0:8765/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "web_search",
      "arguments": {
        "query": "gpt4free library",
        "max_results": 3
      }
    }
  }'
```

## Integration with AI Assistants

The MCP server can be integrated with AI assistants that support the Model Context Protocol standard, allowing them to access gpt4free capabilities in a standardized way.

## Troubleshooting

- Make sure all required dependencies are installed, especially `aiohttp` for HTTP transport
- Ensure the specified port is not already in use
- Check that your firewall allows connections to the specified port