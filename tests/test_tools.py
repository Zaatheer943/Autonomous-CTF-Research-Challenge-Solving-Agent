import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tools.http import HTTPTool
from app.tools.terminal import TerminalTool
from app.tools.files import FilesTool


def test_http_tool_schema():
    tool = HTTPTool()
    schema = tool.get_schema()
    assert "properties" in schema
    assert "method" in schema["properties"]
    assert "url" in schema["properties"]


def test_http_tool_unauthorized_url():
    tool = HTTPTool()
    result = tool.execute({
        "method": "GET",
        "url": "http://evil.com"
    })
    assert not result.success
    assert "not in allowed networks" in result.error


def test_http_tool_relative_url():
    tool = HTTPTool()
    # This will fail because server isn't running, but should pass URL validation
    result = tool.execute({
        "method": "GET",
        "url": "/test"
    })
    # Should attempt the request (will fail due to no server)
    # but should not reject based on URL validation
    assert "allowed networks" not in str(result.error or "")


def test_terminal_tool_schema():
    tool = TerminalTool()
    schema = tool.get_schema()
    assert "properties" in schema
    assert "command" in schema["properties"]


def test_terminal_tool_dangerous_command():
    tool = TerminalTool()
    result = tool.execute({
        "command": "rm -rf /"
    })
    assert not result.success
    assert "dangerous" in result.error


def test_files_tool_schema():
    tool = FilesTool()
    schema = tool.get_schema()
    assert "properties" in schema
    assert "action" in schema["properties"]
    assert "path" in schema["properties"]


def test_files_tool_unauthorized_path():
    tool = FilesTool()
    result = tool.execute({
        "action": "read",
        "path": "C:\\Windows\\System32"
    })
    assert not result.success
    assert "not allowed" in result.error


def test_files_tool_read_nonexistent():
    tool = FilesTool()
    result = tool.execute({
        "action": "read",
        "path": "./nonexistent_file.txt"
    })
    assert not result.success
    assert "not found" in result.error
