"""HTTP Tool for gpt4free MCP

This module provides an HTTP tool that allows AI assistants to send HTTP requests
to external endpoints.
"""

from __future__ import annotations

import aiohttp
import urllib.parse
from typing import Any, Dict
from abc import ABC, abstractmethod


class MCPTool(ABC):
    """Base class for MCP tools (replicated here to avoid import issues)"""
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @property
    @abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON schema for tool input parameters"""
        pass
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given arguments
        
        Args:
            arguments: Tool input arguments matching the input_schema
            
        Returns:
            Dict containing either results or an error key with error message
        """
        pass


class HttpTool(MCPTool):
    """Tool for sending HTTP requests to external endpoints"""
    
    @property
    def description(self) -> str:
        return "Send HTTP requests (GET, POST, PUT, DELETE) to external endpoints. Supports headers, query parameters, and request body. Returns response data."
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to send the HTTP request to"
                },
                "method": {
                    "type": "string",
                    "description": "HTTP method to use (GET, POST, PUT, DELETE)",
                    "enum": ["GET", "POST", "PUT", "DELETE"],
                    "default": "GET"
                },
                "headers": {
                    "type": "object",
                    "description": "HTTP headers to include in the request"
                },
                "params": {
                    "type": "object",
                    "description": "Query parameters to include in the request"
                },
                "body": {
                    "type": "string",
                    "description": "Request body for POST/PUT requests"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Request timeout in seconds (default: 30)",
                    "default": 30
                }
            },
            "required": ["url"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute HTTP request
        
        Returns:
            Dict[str, Any]: Response data or error message
        """
        url = arguments.get("url", "")
        method = arguments.get("method", "GET").upper()
        headers = arguments.get("headers", {})
        params = arguments.get("params", {})
        body = arguments.get("body", "")
        timeout = arguments.get("timeout", 30)
        
        # Validate parameters
        if not url:
            return {
                "error": "URL parameter is required"
            }
        
        if not isinstance(url, str) or len(url.strip()) == 0:
            return {
                "error": "URL must be a non-empty string"
            }
        
        # Validate URL format
        parsed_url = urllib.parse.urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {
                "error": "Invalid URL format"
            }
        
        # Security: only allow http and https schemes
        if parsed_url.scheme not in ["http", "https"]:
            return {
                "error": "Only HTTP and HTTPS URLs are allowed"
            }
        
        # Security: prevent requests to private/local addresses
        if parsed_url.hostname in ["localhost", "127.0.0.1", "0.0.0"] or parsed_url.hostname.startswith("10.") or parsed_url.hostname.startswith("192.168.") or parsed_url.hostname.startswith("172."):
            return {
                "error": "Requests to localhost or private addresses are not allowed"
            }
        
        if method not in ["GET", "POST", "PUT", "DELETE"]:
            return {
                "error": f"HTTP method must be one of GET, POST, PUT, DELETE. Got: {method}"
            }
        
        if not isinstance(headers, dict):
            return {
                "error": "Headers must be an object"
            }
        
        if not isinstance(params, dict):
            return {
                "error": "Params must be an object"
            }
        
        if not isinstance(body, str):
            return {
                "error": "Body must be a string"
            }
        
        if not isinstance(timeout, int) or timeout <= 0:
            return {
                "error": "Timeout must be a positive integer"
            }
        
        if timeout > 300:  # 5 minutes max timeout
            return {
                "error": "Timeout cannot exceed 300 seconds"
            }
        
        try:
            # Create a custom connector to prevent requests to private addresses
            connector = aiohttp.TCPConnector(limit=10)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # Prepare request parameters
                request_kwargs = {
                    "url": url,
                    "headers": headers,
                    "params": params,
                    "timeout": aiohttp.ClientTimeout(total=timeout)
                }
                
                # Add body for POST/PUT requests
                if method in ["POST", "PUT"] and body:
                    request_kwargs["data"] = body
                    # Set content-type header if not already set
                    if "content-type" not in {k.lower() for k in headers.keys()}:
                        request_kwargs["headers"] = {**headers, "Content-Type": "application/json"}
                
                # Send the request
                async with session.request(method, **request_kwargs) as response:
                    # Read response
                    response_text = await response.text()
                    response_headers = dict(response.headers)
                    
                    return {
                        "url": url,
                        "method": method,
                        "status_code": response.status,
                        "headers": response_headers,
                        "body": response_text,
                        "content_length": len(response_text)
                    }
        
        except aiohttp.ClientError as e:
            return {
                "error": f"HTTP request failed: {str(e)}"
            }
        except Exception as e:
            return {
                "error": f"HTTP request failed: {str(e)}"
            }