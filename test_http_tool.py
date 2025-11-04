import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g4f.mcp.http_tool import HttpTool
import asyncio

async def test():
    tool = HttpTool()
    
    # Тест GET запроса
    result1 = await tool.execute({
        'url': 'https://httpbin.org/get',
        'method': 'GET'
    })
    print('GET request result:', result1)
    
    # Тест POST запроса
    result2 = await tool.execute({
        'url': 'https://httpbin.org/post',
        'method': 'POST',
        'headers': {'Content-Type': 'application/json'},
        'body': '{"test": "data", "value": 123}'
    })
    print('POST request result:', result2)

if __name__ == "__main__":
    asyncio.run(test())