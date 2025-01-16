
from controlflow.tools import Tool

tool_registry = {}


def register_tool(tool_name: str, tool_class: type[Tool]):
    """Register a tool in the registry"""
    tool_registry[tool_name] = tool_class


def get_tools():
    """Get all tools"""
    return list(tool_registry.values())


def register_tools(tools: list[type[Tool]]):
    """Register a list of tools in the registry"""
    for tool in tools:
        register_tool(tool.name, tool)


def get_tool(tool_name: str) -> type[Tool]:
    """Get a tool from the registry"""
    return tool_registry[tool_name]


def auto_register_tool(cls):
    """Decorator to automatically register tools"""
    tool_name = getattr(cls, "name", None)
    if tool_name is None:
        pass
    register_tool(tool_name, cls)
    return cls
