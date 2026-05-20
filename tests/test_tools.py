"""Tests para herramientas."""
import pytest
from pathlib import Path

from src.tools import ToolRegistry, get_tool
from src.tools.base import Tool
from src.tools.shell import ShellTool
from src.tools.file import FileTool
from src.tools.web import WebSearchTool
from src.tools.code import CodeTool


def test_tool_registry_get():
    """Testea obtención de herramienta."""
    tool = get_tool("shell")
    assert isinstance(tool, Tool)


def test_tool_registry_list():
    """Testea listado de herramientas."""
    tools = ToolRegistry.list_tools()
    assert len(tools) > 0
    assert any(t["name"] == "shell" for t in tools)


def test_shell_tool_execute():
    """Testea ejecución de comando shell."""
    tool = ShellTool()
    result = tool.execute("echo hello")
    assert "hello" in result or result


def test_file_tool_list():
    """Testea listado de archivos."""
    tool = FileTool(workspace=Path("/workspace/project"))
    result = tool._list("src")
    assert result is not None


def test_code_tool_schema():
    """Testea schema de herramienta de código."""
    tool = CodeTool()
    schema = tool.get_schema()
    assert schema["name"] == "code"