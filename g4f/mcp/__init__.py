"""MCP (Model Context Protocol) Server for gpt4free

This module provides an MCP server implementation that exposes gpt4free capabilities
through the Model Context Protocol standard, allowing AI assistants to access:
- Web search functionality
- Web scraping capabilities  
- Image generation using various providers
"""

from .server import MCPServer
from .tools import MarkItDownTool, TextToAudioTool, WebSearchTool, WebScrapeTool, ImageGenerationTool
from .file_tools import FileReaderTool, FileWriterTool, FileListTool
from .code_execution_tool import CodeExecutionTool, SafeCodeExecutionTool
from .git_tool import GitTool
from .database_tool import DatabaseTool
from .http_tool import HttpTool

__all__ = ['MCPServer', 'MarkItDownTool', 'TextToAudioTool', 'WebSearchTool', 'WebScrapeTool', 'ImageGenerationTool', 'FileReaderTool', 'FileWriterTool', 'FileListTool', 'CodeExecutionTool', 'SafeCodeExecutionTool', 'GitTool', 'DatabaseTool', 'HttpTool']
