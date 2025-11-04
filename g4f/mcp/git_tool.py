"""Git Tool for gpt4free MCP

This module provides a Git tool that allows AI assistants to perform Git operations
like cloning repositories, checking status, committing changes, and pushing updates.
"""

from __future__ import annotations

import os
import subprocess
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


class GitTool(MCPTool):
    """Tool for performing Git operations"""
    
    @property
    def description(self) -> str:
        return "Perform Git operations like cloning, committing, and pushing. Supports common Git commands in a secure environment."
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The Git command to execute (e.g., 'clone', 'status', 'add', 'commit', 'push', 'pull', 'log', 'diff', 'remote')",
                    "enum": ["clone", "status", "add", "commit", "push", "pull", "log", "branch", "checkout", "diff", "remote", "fetch", "merge"]
                },
                "repository_url": {
                    "type": "string",
                    "description": "URL of the Git repository (required for clone command)"
                },
                "local_path": {
                    "type": "string",
                    "description": "Local path for Git operations (required for most commands)"
                },
                "message": {
                    "type": "string",
                    "description": "Commit message (required for commit command)"
                },
                "files": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Files to add or operate on (for add and commit commands)"
                },
                "branch": {
                    "type": "string",
                    "description": "Branch name for checkout or push/pull operations"
                }
            },
            "required": ["command"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Git command
        
        Returns:
            Dict[str, Any]: Git command result or error message
        """
        command = arguments.get("command", "")
        repository_url = arguments.get("repository_url", "")
        local_path = arguments.get("local_path", "")
        message = arguments.get("message", "")
        files = arguments.get("files", [])
        branch = arguments.get("branch", "main")
        
        # Validate command parameter
        if not command:
            return {
                "error": "Command parameter is required"
            }
        
        if not isinstance(command, str):
            return {
                "error": "Command must be a string"
            }
        
        # Security: validate allowed commands
        allowed_commands = ["status", "add", "commit", "push", "pull", "log", "branch", "checkout", "diff", "remote", "fetch", "merge"]
        if command not in allowed_commands and command != "clone":
            return {
                "error": f"Command '{command}' is not allowed. Allowed commands: {allowed_commands + ['clone']}"
            }
        
        try:
            if command == "clone":
                # Validate repository URL and local path
                if not repository_url:
                    return {
                        "error": "repository_url is required for clone command"
                    }
                
                if not local_path:
                    return {
                        "error": "local_path is required for clone command"
                    }
                
                # Security: prevent directory traversal
                local_path_obj = Path(local_path).resolve()
                if ".." in local_path or str(local_path_obj).startswith(".."):
                    return {
                        "error": "Directory traversal not allowed"
                    }
                
                # Security: validate repository URL
                if not (repository_url.startswith("https://") or repository_url.startswith("git@") or repository_url.startswith("http://")):
                    return {
                        "error": "Invalid repository URL format"
                    }
                
                # Execute git clone
                result = subprocess.run(
                    ["git", "clone", repository_url, local_path],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                return {
                    "command": command,
                    "repository_url": repository_url,
                    "local_path": local_path,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
            
            elif command in allowed_commands:
                # Validate local path for other commands
                if not local_path:
                    return {
                        "error": "local_path is required for this command"
                    }
                
                # Security: prevent directory traversal
                local_path_obj = Path(local_path).resolve()
                if ".." in local_path or str(local_path_obj).startswith(".."):
                    return {
                        "error": "Directory traversal not allowed"
                    }
                
                # Check if the directory is a Git repository (except for commands that don't require it)
                requires_git_repo = command not in ["branch", "remote"]
                if requires_git_repo:
                    git_dir = os.path.join(local_path, ".git")
                    if not os.path.exists(git_dir):
                        return {
                            "error": f"Directory '{local_path}' is not a Git repository"
                        }
                
                # Execute the appropriate Git command
                if command == "status":
                    result = subprocess.run(
                        ["git", "-C", local_path, "status", "--porcelain"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                
                elif command == "add":
                    if not files or not isinstance(files, list):
                        # Add all files if none specified
                        cmd = ["git", "-C", local_path, "add", "."]
                    else:
                        # Add specific files
                        cmd = ["git", "-C", local_path, "add"] + files
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                
                elif command == "commit":
                    if not message:
                        return {
                            "error": "message is required for commit command"
                        }
                    
                    result = subprocess.run(
                        ["git", "-C", local_path, "commit", "-m", message],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                
                elif command == "push":
                    cmd = ["git", "-C", local_path, "push"]
                    if branch:
                        cmd.extend(["origin", branch])
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                
                elif command == "pull":
                    cmd = ["git", "-C", local_path, "pull"]
                    if branch:
                        cmd.extend(["origin", branch])
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                
                elif command == "log":
                    result = subprocess.run(
                        ["git", "-C", local_path, "log", "--oneline", "-10"],  # Last 10 commits
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                
                elif command == "branch":
                    cmd = ["git", "-C", local_path, "branch", "-a"] if local_path and os.path.exists(os.path.join(local_path, ".git")) else ["git", "branch", "-a"]
                    if local_path and os.path.exists(os.path.join(local_path, ".git")):
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                    else:
                        # If no local path with .git, run without -C
                        result = subprocess.run(["git", "branch", "-a"], capture_output=True, text=True, timeout=10)
                
                elif command == "checkout":
                    if not branch:
                        return {
                            "error": "branch is required for checkout command"
                        }
                    
                    result = subprocess.run(
                        ["git", "-C", local_path, "checkout", branch],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                
                elif command == "diff":
                    cmd = ["git", "-C", local_path, "diff"]
                    if files and isinstance(files, list):
                        cmd.extend(files)
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                
                elif command == "remote":
                    result = subprocess.run(
                        ["git", "-C", local_path, "remote", "-v"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                
                elif command == "fetch":
                    cmd = ["git", "-C", local_path, "fetch"]
                    if branch:
                        cmd.append(branch)
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                
                elif command == "merge":
                    if not branch:
                        return {
                            "error": "branch is required for merge command"
                        }
                    
                    result = subprocess.run(
                        ["git", "-C", local_path, "merge", branch],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                
                else:
                    return {
                        "error": f"Unsupported command: {command}"
                    }
                
                return {
                    "command": command,
                    "local_path": local_path,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "return_code": result.returncode
                }
            
            else:
                return {
                    "error": f"Unsupported command: {command}"
                }
        
        except subprocess.TimeoutExpired:
            return {
                "error": f"Git command '{command}' timed out"
            }
        except Exception as e:
            return {
                "error": f"Git command failed: {str(e)}"
            }