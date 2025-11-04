from g4f.mcp.file_tools import FileReaderTool
import asyncio

async def test():
    tool = FileReaderTool()
    result = await tool.execute({
        'path': 'README.md'
    })
    print('File read completed successfully')
    print('Result keys:', list(result.keys()))
    if 'error' in result:
        print('Error occurred:', result['error'])
    else:
        print('File size:', result.get('size', 'N/A'))
        print('Content preview (first 200 chars):', repr(result.get('content', '')[:200]))
    return result

if __name__ == "__main__":
    asyncio.run(test())