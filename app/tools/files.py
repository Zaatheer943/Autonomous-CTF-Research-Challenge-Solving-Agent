import os
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.base import BaseTool, ToolResult
from app.config import settings


class FilesTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="files",
            description="Read files and list directories. Use for file system reconnaissance and analysis."
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["read", "list", "search"],
                    "description": "File action to perform"
                },
                "path": {
                    "type": "string",
                    "description": "File or directory path"
                },
                "pattern": {
                    "type": "string",
                    "description": "Search pattern (for search action)"
                }
            },
            "required": ["action", "path"]
        }

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        try:
            action = parameters.get("action", "read")
            path = parameters.get("path", "")

            # Security: Only allow access to specific directories
            if not self._is_path_allowed(path):
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Path {path} is not allowed"
                )

            if action == "read":
                return self._read_file(path)
            elif action == "list":
                return self._list_directory(path)
            elif action == "search":
                pattern = parameters.get("pattern", "*")
                return self._search_files(path, pattern)
            else:
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Unknown action: {action}"
                )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )

    def _read_file(self, path: str) -> ToolResult:
        try:
            file_path = Path(path)
            if not file_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"File not found: {path}"
                )

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Limit output size
            if len(content) > 10000:
                content = content[:10000] + "\n... (truncated)"

            return ToolResult(
                success=True,
                output=content
            )

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )

    def _list_directory(self, path: str) -> ToolResult:
        try:
            dir_path = Path(path)
            if not dir_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Directory not found: {path}"
                )

            items = []
            for item in dir_path.iterdir():
                item_type = "DIR" if item.is_dir() else "FILE"
                items.append(f"{item_type}: {item.name}")

            output = "\n".join(items) if items else "Directory is empty"
            return ToolResult(success=True, output=output)

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )

    def _search_files(self, path: str, pattern: str) -> ToolResult:
        try:
            dir_path = Path(path)
            if not dir_path.exists():
                return ToolResult(
                    success=False,
                    output="",
                    error=f"Directory not found: {path}"
                )

            matches = list(dir_path.glob(pattern))
            output = "\n".join(str(m) for m in matches) if matches else "No matches found"
            return ToolResult(success=True, output=output)

        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )

    def _is_path_allowed(self, path: str) -> bool:
        # For MVP, only allow access to data directory and current directory
        try:
            abs_path = Path(path).resolve()
            cwd = Path.cwd()

            # Allow data directory
            data_dir = cwd / "data"
            if data_dir in abs_path.parents or abs_path == data_dir:
                return True

            # Allow current directory (with restrictions)
            if cwd in abs_path.parents or abs_path == cwd:
                # Don't allow system directories
                forbidden = ["Windows", "Program Files", "System32"]
                for forbidden_dir in forbidden:
                    if forbidden_dir in str(abs_path):
                        return False
                return True

            return False
        except Exception:
            return False
