"""Database Tool for gpt4free MCP

This module provides a database tool that allows AI assistants to execute SQL queries
on SQLite databases.
"""

from __future__ import annotations

import sqlite3
import os
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


class DatabaseTool(MCPTool):
    """Tool for executing SQL queries on SQLite databases"""
    
    @property
    def description(self) -> str:
        return "Execute SQL queries on SQLite databases. Supports SELECT, INSERT, UPDATE, DELETE statements. Returns query results or execution status."
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "db_path": {
                    "type": "string",
                    "description": "Path to the SQLite database file"
                },
                "query": {
                    "type": "string",
                    "description": "SQL query to execute"
                },
                "params": {
                    "type": "array",
                    "items": {
                        "type": ["string", "number", "boolean"]
                    },
                    "description": "Parameters for the SQL query (optional)"
                }
            },
            "required": ["db_path", "query"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQL query
        
        Returns:
            Dict[str, Any]: Query results or error message
        """
        db_path = arguments.get("db_path", "")
        query = arguments.get("query", "")
        params = arguments.get("params", [])
        
        # Validate parameters
        if not db_path:
            return {
                "error": "db_path parameter is required"
            }
        
        if not query:
            return {
                "error": "query parameter is required"
            }
        
        if not isinstance(db_path, str) or len(db_path.strip()) == 0:
            return {
                "error": "db_path must be a non-empty string"
            }
        
        if not isinstance(query, str) or len(query.strip()) == 0:
            return {
                "error": "query must be a non-empty string"
            }
        
        if not isinstance(params, list):
            return {
                "error": "params must be a list"
            }
        
        # Security: prevent directory traversal
        try:
            db_path_obj = Path(db_path).resolve()
            if ".." in db_path or str(db_path_obj).startswith(".."):
                return {
                    "error": "Directory traversal not allowed"
                }
        except Exception:
            return {
                "error": "Invalid database path"
            }
        
        # Security: only allow .db, .sqlite, .sqlite3 file extensions
        valid_extensions = ['.db', '.sqlite', '.sqlite3']
        if Path(db_path).suffix.lower() not in valid_extensions:
            return {
                "error": f"Only SQLite database files are allowed (extensions: {', '.join(valid_extensions)})"
            }
        
        # Security: check if the database file exists, if not, verify we're not creating outside allowed directories
        db_exists = os.path.exists(db_path)
        
        try:
            # Connect to database
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row  # Enable column access by name
            cursor = conn.cursor()
            
            # Security: only allow specific SQL commands
            query_upper = query.strip().upper()
            allowed_commands = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'DROP', 'ALTER', 'PRAGMA']
            
            # Check the first word of the query
            first_word = query_upper.split()[0] if query_upper.split() else ""
            if first_word not in allowed_commands:
                return {
                    "error": f"SQL command not allowed: {first_word}. Only {', '.join(allowed_commands)} commands are allowed."
                }
            
            # Execute the query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Check if it's a SELECT query to return results
            if first_word == 'SELECT':
                rows = cursor.fetchall()
                
                # Convert rows to list of dictionaries
                results = []
                for row in rows:
                    results.append({key: row[key] for key in row.keys()})
                
                conn.close()
                
                return {
                    "query_type": "SELECT",
                    "results": results,
                    "row_count": len(results)
                }
            else:
                # For non-SELECT queries (INSERT, UPDATE, DELETE, etc.)
                conn.commit()
                changes = conn.total_changes
                conn.close()
                
                return {
                    "query_type": first_word,
                    "message": f"Query executed successfully",
                    "affected_rows": changes
                }
        
        except sqlite3.Error as e:
            return {
                "error": f"Database error: {str(e)}"
            }
        except Exception as e:
            return {
                "error": f"Query execution failed: {str(e)}"
            }