"""Code Generation Tool for gpt4free MCP

This module provides a code generation tool that uses gpt4free's capabilities
to generate code based on user prompts.
"""

from __future__ import annotations

from typing import Any, Dict
from abc import ABC, abstractmethod

from ..client import AsyncClient


class CodeGenerationTool(ABC):
    """Base class for code generation tools"""
    
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


class CodeGenerationToolImpl(CodeGenerationTool):
    """Code generation tool using gpt4free's AI capabilities"""
    
    @property
    def description(self) -> str:
        return "Generate code based on a text prompt using AI. Supports various programming languages and frameworks. Returns the generated code."
    
    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The text prompt describing the code to generate"
                },
                "model": {
                    "type": "string",
                    "description": "The AI model to use for code generation (default: gpt-4o)",
                    "default": "gpt-4o"
                },
                "language": {
                    "type": "string",
                    "description": "The programming language for the generated code (e.g., python, javascript, java, etc.)",
                    "default": "python"
                },
                "max_tokens": {
                    "type": "integer",
                    "description": "Maximum number of tokens to generate (default: 2048)",
                    "default": 2048
                }
            },
            "required": ["prompt"]
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code generation
        
        Returns:
            Dict[str, Any]: Generated code or error message
        """
        prompt = arguments.get("prompt", "")
        model = arguments.get("model", "gpt-4o")
        language = arguments.get("language", "python")
        max_tokens = arguments.get("max_tokens", 2048)
        
        if not prompt:
            return {
                "error": "Prompt parameter is required"
            }
        
        try:
            # Enhance the prompt with language-specific instructions
            enhanced_prompt = f"Generate code in {language} language: {prompt}"
            
            # Generate code using gpt4free client
            client = AsyncClient()
            
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": enhanced_prompt}],
                max_tokens=max_tokens
            )
            
            # Get the generated code
            if not response or not response.choices:
                return {
                    "error": "Code generation failed: No response from provider"
                }
            
            generated_code = response.choices[0].message.content
            
            if not generated_code:
                return {
                    "error": "Code generation failed: No code in response"
                }
            
            return {
                "prompt": prompt,
                "model": model,
                "language": language,
                "generated_code": generated_code,
                "token_count": len(generated_code.split())
            }
        
        except Exception as e:
            return {
                "error": f"Code generation failed: {str(e)}"
            }