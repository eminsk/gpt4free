import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g4f.mcp.server import main

if __name__ == "__main__":
    # Запускаем MCP сервер в stdio режиме
    main(http=False)