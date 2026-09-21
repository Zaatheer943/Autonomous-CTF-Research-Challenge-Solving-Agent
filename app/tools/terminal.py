import subprocess
import docker
from typing import Dict, Any
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.base import BaseTool, ToolResult
from app.config import settings


class TerminalTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="terminal",
            description="Execute terminal commands in a Docker container sandbox. Use for reconnaissance and analysis."
        )

    def get_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to execute in the terminal"
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory for the command (default: /app)"
                }
            },
            "required": ["command"]
        }

    def execute(self, parameters: Dict[str, Any]) -> ToolResult:
        try:
            command = parameters.get("command", "")
            working_dir = parameters.get("working_dir", "/app")

            # For MVP, we'll use subprocess with strict limitations
            # In production, this should use Docker containers
            if not self._is_command_safe(command):
                return ToolResult(
                    success=False,
                    output="",
                    error="Command contains potentially dangerous operations"
                )

            try:
                # Try to use Docker if available
                client = docker.from_env()
                result = client.containers.run(
                    "alpine:latest",
                    command=command,
                    working_dir=working_dir,
                    remove=True,
                    timeout=settings.command_timeout,
                    stdout=True,
                    stderr=True
                )
                output = result.decode('utf-8', errors='ignore')
                return ToolResult(success=True, output=output)

            except Exception as docker_error:
                # Fallback to subprocess with limitations
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=settings.command_timeout
                )

                output = result.stdout
                if result.stderr:
                    output += f"\nSTDERR: {result.stderr}"

                return ToolResult(
                    success=result.returncode == 0,
                    output=output,
                    error=result.stderr if result.returncode != 0 else None
                )

        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                output="",
                error="Command timeout exceeded"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                output="",
                error=str(e)
            )

    def _is_command_safe(self, command: str) -> bool:
        # Basic safety checks
        dangerous_commands = [
            "rm -rf /",
            "mkfs",
            "dd if=",
            ":(){ :|:& };:",
            "chmod 777 /",
            "chown root",
            "sudo rm",
            "format",
            "del /f"
        ]

        command_lower = command.lower()
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                return False

        return True
