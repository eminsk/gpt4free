import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g4f.mcp.database_tool import DatabaseTool
import asyncio
import tempfile

async def test():
    tool = DatabaseTool()
    
    # Создаем временный файл базы данных для тестирования
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as temp_db:
        temp_db_path = temp_db.name
    
    try:
        # Тест 1: Создание таблицы
        result1 = await tool.execute({
            'db_path': temp_db_path,
            'query': 'CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, email TEXT)'
        })
        print('Create table result:', result1)
        
        # Тест 2: Вставка данных
        result2 = await tool.execute({
            'db_path': temp_db_path,
            'query': 'INSERT INTO users (name, email) VALUES (?, ?)',
            'params': ['John Doe', 'john@example.com']
        })
        print('Insert result:', result2)
        
        # Тест 3: Выборка данных
        result3 = await tool.execute({
            'db_path': temp_db_path,
            'query': 'SELECT * FROM users'
        })
        print('Select result:', result3)
        
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_db_path):
            os.remove(temp_db_path)

if __name__ == "__main__":
    asyncio.run(test())