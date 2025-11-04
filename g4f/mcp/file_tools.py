"""File Tools for gpt4free MCP

This module provides MCP file-related tool implementations:
- File reading tool
- File writing tool
- File listing tool
"""

from __future__ import annotations

import os
import json
from typing import Any, Dict
from abc import ABC, abstractmethod
from pathlib import Path


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


class FileReaderTool(MCPTool):
    """Tool for reading file contents"""
    
    @property
    def description(self) -> str:
        return "Read the contents of a file from the filesystem. Returns the file content as text."
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to read"
                },
                "max_size": {
                    "type": "integer",
                    "description": "Maximum file size to read in bytes (default: 1048576 = 1MB)",
                    "default": 1048576
                }
            },
            "required": ["path"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file reading
        
        Returns:
            Dict[str, Any]: File content or error message
        """
        path = arguments.get("path", "")
        max_size = arguments.get("max_size", 1048576)
        
        # Validate parameters
        if not path:
            return {
                "error": "Path parameter is required"
            }
        
        if not isinstance(path, str) or len(path.strip()) == 0:
            return {
                "error": "Path must be a non-empty string"
            }
        
        if not isinstance(max_size, int) or max_size <= 0:
            return {
                "error": "max_size must be a positive integer"
            }
        
        try:
            # Check if path is within allowed directories
            file_path = Path(path).resolve()
            
            # Security: prevent directory traversal
            if ".." in path or str(file_path).startswith(".."):
                return {
                    "error": "Directory traversal not allowed"
                }
            
            # Check file exists
            if not file_path.exists():
                return {
                    "error": f"File does not exist: {path}"
                }
            
            # Check if it's a file (not a directory)
            if not file_path.is_file():
                return {
                    "error": f"Path is not a file: {path}"
                }
            
            # Check file size
            file_size = file_path.stat().st_size
            if file_size > max_size:
                return {
                    "error": f"File size {file_size} bytes exceeds maximum allowed size of {max_size} bytes"
                }
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return {
                "path": path,
                "content": content,
                "size": file_size,
                "encoding": "utf-8"
            }
        
        except UnicodeDecodeError:
            return {
                "error": f"File at {path} is not a text file or uses unsupported encoding"
            }
        except PermissionError:
            return {
                "error": f"Permission denied when reading file: {path}"
            }
        except Exception as e:
            return {
                "error": f"File reading failed: {str(e)}"
            }


class FileWriterTool(MCPTool):
    """Tool for writing content to a file"""
    
    @property
    def description(self) -> str:
        return "Write content to a file in the filesystem. Creates or overwrites the file with the provided content."
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The path to the file to write"
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file"
                },
                "overwrite": {
                    "type": "boolean",
                    "description": "Whether to overwrite existing file (default: true)",
                    "default": True
                }
            },
            "required": ["path", "content"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file writing
        
        Returns:
            Dict[str, Any]: Success message or error message
        """
        path = arguments.get("path", "")
        content = arguments.get("content", "")
        overwrite = arguments.get("overwrite", True)
        
        # Validate parameters
        if not path:
            return {
                "error": "Path parameter is required"
            }
        
        if not isinstance(path, str) or len(path.strip()) == 0:
            return {
                "error": "Path must be a non-empty string"
            }
        
        if not isinstance(content, str):
            return {
                "error": "Content must be a string"
            }
        
        if not isinstance(overwrite, bool):
            return {
                "error": "Overwrite must be a boolean"
            }
        
        try:
            # Check if path is within allowed directories
            file_path = Path(path).resolve()
            
            # Security: prevent directory traversal
            if ".." in path or str(file_path).startswith(".."):
                return {
                    "error": "Directory traversal not allowed"
                }
            
            # Check if file exists
            if file_path.exists() and not overwrite:
                return {
                    "error": f"File already exists and overwrite is false: {path}"
                }
            
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write content to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "path": path,
                "message": f"Successfully wrote {len(content)} characters to file",
                "size": len(content)
            }
        
        except PermissionError:
            return {
                "error": f"Permission denied when writing to file: {path}"
            }
        except Exception as e:
            return {
                "error": f"File writing failed: {str(e)}"
            }


class FileListTool(MCPTool):
    """Tool for listing files in a directory"""
    
    @property
    def description(self) -> str:
        return "List files and directories in a specified directory. Returns information about each item including type and size."
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "The directory path to list"
                },
                "recursive": {
                    "type": "boolean",
                    "description": "Whether to list files recursively (default: false)",
                    "default": False
                },
                "max_items": {
                    "type": "integer",
                    "description": "Maximum number of items to return (default: 100)",
                    "default": 100
                }
            },
            "required": ["path"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file listing
        
        Returns:
            Dict[str, Any]: List of files/directories or error message
        """
        path = arguments.get("path", "")
        recursive = arguments.get("recursive", False)
        max_items = arguments.get("max_items", 100)
        
        # Validate parameters
        if not path:
            return {
                "error": "Path parameter is required"
            }
        
        if not isinstance(path, str) or len(path.strip()) == 0:
            return {
                "error": "Path must be a non-empty string"
            }
        
        if not isinstance(recursive, bool):
            return {
                "error": "Recursive must be a boolean"
            }
        
        if not isinstance(max_items, int) or max_items <= 0:
            return {
                "error": "max_items must be a positive integer"
            }
        
        try:
            # Check if path is within allowed directories
            dir_path = Path(path).resolve()
            
            # Security: prevent directory traversal
            if ".." in path or str(dir_path).startswith(".."):
                return {
                    "error": "Directory traversal not allowed"
                }
            
            # Check if path exists and is a directory
            if not dir_path.exists():
                return {
                    "error": f"Directory does not exist: {path}"
                }
            
            if not dir_path.is_dir():
                return {
                    "error": f"Path is not a directory: {path}"
                }
            
            # List files and directories
            items = []
            
            if recursive:
                for item_path in dir_path.rglob("*"):
                    if len(items) >= max_items:
                        break
                    relative_path = item_path.relative_to(dir_path)
                    item_info = {
                        "name": item_path.name,
                        "path": str(relative_path),
                        "type": "directory" if item_path.is_dir() else "file"
                    }
                    if item_path.is_file():
                        item_info["size"] = item_path.stat().st_size
                    items.append(item_info)
            else:
                for item_path in dir_path.iterdir():
                    if len(items) >= max_items:
                        break
                    item_info = {
                        "name": item_path.name,
                        "path": item_path.name,
                        "type": "directory" if item_path.is_dir() else "file"
                    }
                    if item_path.is_file():
                        item_info["size"] = item_path.stat().st_size
                    items.append(item_info)
            
            return {
                "path": path,
                "items": items,
                "total_items": len(items)
            }
        
        except PermissionError:
            return {
                "error": f"Permission denied when accessing directory: {path}"
            }
        except Exception as e:
            return {
                "error": f"File listing failed: {str(e)}"
            }