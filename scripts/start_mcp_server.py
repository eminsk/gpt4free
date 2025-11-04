#!/usr/bin/env python3
"""
Script to start the gpt4free MCP (Model Context Protocol) server in HTTP mode.

This script provides a convenient way to launch the MCP server that exposes
gpt4free capabilities through the Model Context Protocol standard.
"""

import sys
import argparse
from g4f.mcp.server import main


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Start gpt4free MCP (Model Context Protocol) server in HTTP mode"
    )
    parser.add_argument(
        "--http",
        action="store_true",
        default=True,
        help="Run server in HTTP mode (default: True)"
    )
    parser.add_argument(
        "--stdio",
        action="store_true",
        default=False,
        help="Run server in stdio mode (default: False)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0",
        help="Host to bind the HTTP server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8765,
        help="Port to bind the HTTP server to (default: 8765)"
    )
    parser.add_argument(
        "--origin",
        type=str,
        default=None,
        help="Origin URL for requests (optional)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration file (optional)"
    )
    
    return parser.parse_args()


def main_cli():
    """Main entry point for the CLI"""
    args = parse_arguments()
    
    # Determine run mode
    if args.stdio:
        print("Starting gpt4free MCP server in stdio mode")
        http_mode = False
    else:
        print(f"Starting gpt4free MCP server on http://{args.host}:{args.port}")
        print("Available endpoints:")
        print(f"  MCP endpoint: http://{args.host}:{args.port}/mcp")
        print(f"  Health check: http://{args.host}:{args.port}/health")
        print("Press Ctrl+C to stop the server")
        http_mode = True
    
    try:
        main(
            http=http_mode,
            host=args.host,
            port=args.port,
            origin=args.origin
        )
    except KeyboardInterrupt:
        print("\nShutting down MCP server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting MCP server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main_cli()