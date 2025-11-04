import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g4f.mcp.git_tool import GitTool
import asyncio

async def test():
    tool = GitTool()
    # Тестируем команду status с текущей директорией
    result = await tool.execute({
        'command': 'status',
        'local_path': '.'
    })
    print('Git tool result:', result)
    return result

if __name__ == "__main__":
    asyncio.run(test())