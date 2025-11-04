import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g4f.mcp.code_execution_tool import SafeCodeExecutionTool
import asyncio

async def test_security():
    tool = SafeCodeExecutionTool()
    
    # Тестируем различные потенциально опасные команды
    dangerous_codes = [
        "import os; os.system('echo vulnerable')",
        "__import__('os').system('echo vulnerable')",
        "eval('print(\"dangerous\")')",
        "exec('print(\"dangerous\")')",
        "import subprocess; subprocess.run(['echo', 'dangerous'])",
        "getattr(__import__('os'), 'system')('echo vulnerable')",
        "import sqlite3",
        "open('/etc/passwd', 'r')",
        "with open('test.txt', 'w') as f: f.write('test')",
        "__import__('subprocess').run(['ls'])",
        "import sys; sys.modules['os']",
        "[x for x in ().__class__.__bases__[0].__subclasses__() if x.__name__ == 'file'][0]('/etc/passwd')"
    ]
    
    print("Testing security improvements...")
    
    for i, code in enumerate(dangerous_codes):
        print(f"\nTest {i+1}: {code[:50]}...")
        result = await tool.execute({"code": code})
        if "error" in result:
            print(f"  [OK] Blocked: {result['error'][:60]}...")
        else:
            print(f"  [FAIL] Not blocked: {result}")
    
    # Тестируем безопасный код
    print(f"\nTesting safe code...")
    safe_code = "x = 5\ny = 10\nresult = x + y\nprint(f'Result: {result}')"
    result = await tool.execute({"code": safe_code})
    if "error" in result:
        print(f"  [FAIL] Safe code blocked: {result['error']}")
    else:
        print(f"  [OK] Safe code executed successfully")
        print(f"    Result: {result.get('result', 'N/A')}")

if __name__ == "__main__":
    asyncio.run(test_security())