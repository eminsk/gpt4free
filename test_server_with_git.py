import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g4f.mcp.server import MCPServer

def test():
    server = MCPServer()
    print('MCP Server created successfully')
    print('Available tools:', list(server.tools.keys()))
    
    # Проверим, что git_tool есть в списке инструментов
    if 'git_tool' in server.tools:
        print('[OK] Git tool is available in server')
        git_tool = server.tools['git_tool']
        print('Git tool description:', git_tool.description)
        print('Git tool input schema keys:', list(git_tool.input_schema.keys()))
    else:
        print('[ERROR] Git tool is NOT available in server')
    
    return server

if __name__ == "__main__":
    test()