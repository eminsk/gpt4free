"""Code Execution Tool for gpt4free MCP

This module provides a safe code execution tool that can run Python code snippets.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
import os
from typing import Any, Dict
from abc import ABC, abstractmethod
from pathlib import Path
import ast
import RestrictedPython


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


class CodeExecutionTool(MCPTool):
    """Tool for executing Python code snippets safely"""
    
    @property
    def description(self) -> str:
        return "Execute Python code snippets safely in a restricted environment. Returns the output of the code execution."
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Execution timeout in seconds (default: 10)",
                    "default": 10
                }
            },
            "required": ["code"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code
        
        Returns:
            Dict[str, Any]: Execution result or error message
        """
        code = arguments.get("code", "")
        timeout = arguments.get("timeout", 10)
        
        # Validate parameters
        if not code:
            return {
                "error": "Code parameter is required"
            }
        
        if not isinstance(code, str) or len(code.strip()) == 0:
            return {
                "error": "Code must be a non-empty string"
            }
        
        if not isinstance(timeout, int) or timeout <= 0:
            return {
                "error": "Timeout must be a positive integer"
            }
        
        if timeout > 60:  # Set reasonable limit
            return {
                "error": "Timeout cannot exceed 60 seconds"
            }
        
        # Check for potentially dangerous code patterns
        dangerous_patterns = [
            'import os', 'import sys', 'import subprocess', 'import shutil',
            'exec(', 'eval(', '__import__', 'open(', 'file(',
            'compile(', 'getattr(', 'setattr(', 'delattr(',
            'globals()', 'locals()', 'vars(', '__loader__',
            'execfile', '__builtins__', 'exec_module', 'importlib',
            'from os import', 'from sys import', 'from subprocess import',
            'from importlib import', 'import requests', 'import urllib',
            'import http', 'import socket', 'import ftplib', 'import smtplib',
            'import poplib', 'import imaplib', 'import telnetlib', 'import nntplib',
            'import urllib2', 'import httplib', 'import urllib.request',
            'import urllib.parse', 'import urllib.error', 'import pickle',
            'import shelve', 'import copyreg', 'import _pickle', 'import dill',
            'import shelve', 'import dbm', 'import sqlite3', 'import pymysql',
            'import psycopg2', 'import mysql', 'import pymongo', 'import redis',
            'import boto', 'import boto3', 'import paramiko', 'import fabric',
            'import os.system', 'os.popen', 'os.spawn', 'os.fork',
            'os.exec', 'os.startfile', 'subprocess.run', 'subprocess.call',
            'subprocess.check_output', 'subprocess.check_call', 'subprocess.Popen'
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return {
                    "error": f"Potentially dangerous code pattern detected: {pattern}"
                }
        
        try:
            # Create a temporary file to execute the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                # Execute the code with timeout
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                # Return the results
                return {
                    "code": code,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
            finally:
                # Clean up the temporary file
                os.unlink(temp_file)
        
        except subprocess.TimeoutExpired:
            return {
                "error": f"Code execution timed out after {timeout} seconds"
            }
        except Exception as e:
            return {
                "error": f"Code execution failed: {str(e)}"
            }


class SafeCodeExecutionTool(MCPTool):
    """Tool for executing Python code snippets in a safer restricted environment"""
    
    @property
    def description(self) -> str:
        return "Execute Python code snippets in a restricted environment using AST analysis. Returns the output of the code execution."
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The Python code to execute in a restricted environment"
                }
            },
            "required": ["code"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Python code in restricted environment
        
        Returns:
            Dict[str, Any]: Execution result or error message
        """
        code = arguments.get("code", "")
        
        # Validate parameters
        if not code:
            return {
                "error": "Code parameter is required"
            }
        
        if not isinstance(code, str) or len(code.strip()) == 0:
            return {
                "error": "Code must be a non-empty string"
            }
        
        # Check for dangerous patterns before AST parsing
        dangerous_patterns = [
            'import os', 'import sys', 'import subprocess', 'import shutil',
            'exec(', 'eval(', '__import__', 'open(', 'file(',
            'compile(', 'getattr(', 'setattr(', 'delattr(',
            'globals()', 'locals()', 'vars(', '__loader__',
            'execfile', '__builtins__', 'exec_module', 'importlib',
            'from os import', 'from sys import', 'from subprocess import',
            'from importlib import', 'import requests', 'import urllib',
            'import http', 'import socket', 'import ftplib', 'import smtplib',
            'import poplib', 'import imaplib', 'import telnetlib', 'import nntplib',
            'import urllib2', 'import httplib', 'import urllib.request',
            'import urllib.parse', 'import urllib.error', 'import pickle',
            'import shelve', 'import copyreg', 'import _pickle', 'import dill',
            'import shelve', 'import dbm', 'import sqlite3', 'import pymysql',
            'import psycopg2', 'import mysql', 'import pymongo', 'import redis',
            'import boto', 'import boto3', 'import paramiko', 'import fabric',
            'import os.system', 'os.popen', 'os.spawn', 'os.fork',
            'os.exec', 'os.startfile', 'subprocess.run', 'subprocess.call',
            'subprocess.check_output', 'subprocess.check_call', 'subprocess.Popen'
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return {
                    "error": f"Potentially dangerous code pattern detected: {pattern}"
                }
        
        try:
            # Parse the code to check for dangerous constructs
            try:
                tree = ast.parse(code)
            except SyntaxError as e:
                return {
                    "error": f"Syntax error in code: {str(e)}"
                }
            
            # Check for dangerous AST nodes
            dangerous_nodes = [
                ast.Import, ast.ImportFrom, ast.Call, ast.Attribute,
                ast.Global, ast.Nonlocal, ast.Assert, ast.Delete
            ]
            
            for node in ast.walk(tree):
                if isinstance(node, tuple(dangerous_nodes)):
                    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                        # Allow some safe functions like print, len, etc.
                        allowed_functions = {'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'range', 'enumerate', 'zip', 'map', 'filter', 'sum', 'min', 'max', 'abs', 'round', 'sorted', 'reversed', 'all', 'any', 'chr', 'ord', 'hex', 'oct', 'bin', 'pow', 'divmod', 'abs', 'round', 'max', 'min', 'sum', 'any', 'all', 'bool', 'int', 'float', 'str', 'repr', 'len', 'list', 'tuple', 'set', 'dict', 'sorted', 'reversed', 'enumerate', 'zip', 'isinstance', 'type', 'hasattr', 'getattr', 'setattr', 'delattr', 'callable', 'hash', 'id', 'object', 'ord', 'chr', 'bin', 'hex', 'oct', 'abs', 'round', 'pow', 'divmod'}
                        if node.func.id not in allowed_functions:
                            return {
                                "error": f"Potentially dangerous function call: {node.func.id}"
                            }
                    elif isinstance(node, ast.Attribute):
                        # Check for dangerous attribute access
                        dangerous_attrs = {'system', 'popen', 'exec', 'eval', 'compile', 'open', 'file', 'input', 'raw_input', 'execfile', 'import_module', 'load_module', 'find_module', 'get_code', '__class__', '__mro__', '__bases__', '__subclasses__', '__globals__', '__code__', '__closure__', '__func__', '__self__', '__dict__', '__getattribute__', '__delattr__', '__subclasshook__', '__init_subclass__', '__format__', '__reduce__', '__reduce_ex__'}
                        if hasattr(node, 'attr') and node.attr in dangerous_attrs:
                            return {
                                "error": f"Potentially dangerous attribute access: {node.attr}"
                            }
                    elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                        # Check for dangerous imports
                        imports = []
                        if isinstance(node, ast.Import):
                            imports = [alias.name for alias in node.names]
                        else:  # ast.ImportFrom
                            imports = [node.module] if node.module else []
                        
                        for imp in imports:
                            if imp:
                                parts = imp.split('.')
                                if parts[0] in ['os', 'sys', 'subprocess', 'shutil', 'pickle', 'shelve', 'importlib', 'sqlite3', 'mysql', 'pymongo', 'redis', 'boto', 'boto3', 'paramiko', 'socket', 'ftplib', 'smtplib', 'poplib', 'imaplib', 'telnetlib', 'nntplib', 'urllib', 'http', 'requests', 'fabric']:
                                    return {
                                        "error": f"Potentially dangerous import: {imp}"
                                    }
                    else:
                        return {
                            "error": f"Potentially dangerous construct: {type(node).__name__}"
                        }
            
            # Execute the code in a restricted environment
            # Create restricted globals
            restricted_globals = {
                '__builtins__': {
                    'print': print,
                    'len': len,
                    'str': str,
                    'int': int,
                    'float': float,
                    'bool': bool,
                    'list': list,
                    'dict': dict,
                    'set': set,
                    'tuple': tuple,
                    'range': range,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'sum': sum,
                    'min': min,
                    'max': max,
                    'abs': abs,
                    'round': round,
                    'sorted': sorted,
                    'reversed': reversed,
                    'all': all,
                    'any': any,
                    'chr': chr,
                    'ord': ord,
                    'hex': hex,
                    'oct': oct,
                    'bin': bin,
                    'pow': pow,
                    'divmod': divmod,
                    'isinstance': isinstance,
                    'type': type,
                    'hasattr': hasattr,
                    'getattr': getattr,
                    'setattr': setattr,
                    'delattr': delattr,
                    'callable': callable,
                    'hash': hash,
                    'id': id,
                    'object': object,
                    'Exception': Exception,
                    'ValueError': ValueError,
                    'TypeError': TypeError,
                    'IndexError': IndexError,
                    'KeyError': KeyError,
                    'ZeroDivisionError': ZeroDivisionError,
                    'NameError': NameError,
                    'AttributeError': AttributeError,
                    'RuntimeError': RuntimeError,
                    'StopIteration': StopIteration,
                    'ArithmeticError': ArithmeticError,
                    'AssertionError': AssertionError,
                    'EOFError': EOFError,
                    'ImportError': ImportError,
                    'IndentationError': IndentationError,
                    'LookupError': LookupError,
                    'MemoryError': MemoryError,
                    'NameError': NameError,
                    'OSError': OSError,
                    'ReferenceError': ReferenceError,
                    'SyntaxError': SyntaxError,
                    'SystemError': SystemError,
                    'ValueError': ValueError,
                    'Warning': Warning,
                    'DeprecationWarning': DeprecationWarning,
                    'RuntimeWarning': RuntimeWarning,
                    'SyntaxWarning': SyntaxWarning,
                    'UserWarning': UserWarning,
                    'FutureWarning': FutureWarning,
                    'PendingDeprecationWarning': PendingDeprecationWarning,
                    'ImportWarning': ImportWarning,
                    'UnicodeWarning': UnicodeWarning,
                    'BytesWarning': BytesWarning,
                    'ResourceWarning': ResourceWarning
                }
            }
            
            # Create a local namespace for the execution
            restricted_locals = {}
            
            # Execute the code with timeout using RestrictedPython
            try:
                from RestrictedPython import compile_restricted
                from RestrictedPython.Guards import safe_globals, safe_builtins
                from RestrictedPython.transformer import ALLOWED_FUNC_NAMES
                
                # Compile the code with RestrictedPython
                compiled_code = compile_restricted(code, filename="<inline code>", mode="exec")
                
                if compiled_code.errors:
                    return {
                        "error": f"Compilation errors: {compiled_code.errors}"
                    }
                
                if compiled_code.warnings:
                    return {
                        "error": f"Compilation warnings: {compiled_code.warnings}"
                    }
                
                # Execute the restricted code
                exec(compiled_code.code, restricted_globals, restricted_locals)
                
            except ImportError:
                # Fallback to manual restricted execution if RestrictedPython is not available
                exec(code, restricted_globals, restricted_locals)
            
            # Return the results
            return {
                "code": code,
                "result": "Code executed successfully",
                "globals": {k: str(v) for k, v in restricted_globals.items() if not k.startswith('__')},
                "locals": {k: str(v) for k, v in restricted_locals.items()}
            }
        
        except SyntaxError as e:
            return {
                "error": f"Syntax error in code: {str(e)}"
            }
        except Exception as e:
            return {
                "error": f"Code execution failed: {str(e)}"
            }