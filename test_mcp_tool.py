from g4f.mcp.code_generation_tool import CodeGenerationToolImpl
import asyncio

async def test():
    tool = CodeGenerationToolImpl()
    result = await tool.execute({
        'prompt': 'Write a simple Python function that adds two numbers',
        'language': 'python',
        'max_tokens': 200
    })
    print('Code generation result:', result)
    return result

if __name__ == "__main__":
    asyncio.run(test())