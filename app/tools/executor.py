from typing import Dict, Any, List
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.http import HTTPTool
from app.tools.terminal import TerminalTool
from app.tools.browser import BrowserTool
from app.tools.files import FilesTool
from app.tools.base import ToolResult


class ToolExecutor:
    def __init__(self, target_url: str):
        self.target_url = target_url
        self.tools = {
            "http_request": HTTPTool(),
            "terminal": TerminalTool(),
            "browser": BrowserTool(),
            "files": FilesTool()
        }

    def get_available_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_dict() for tool in self.tools.values()]

    def execute(self, tool_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        if tool_name not in self.tools:
            return {
                "success": False,
                "output": "",
                "error": f"Unknown tool: {tool_name}"
            }

        tool = self.tools[tool_name]
        result: ToolResult = tool.execute(parameters)

        return {
            "success": result.success,
            "output": result.output,
            "error": result.error,
            "metadata": result.metadata
        }
