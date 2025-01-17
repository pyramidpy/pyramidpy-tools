from fastmcp import FastMCP
from pyramidpy_tools.toolkit import Toolkit
import inspect
from functools import wraps


def create_mcp_from_toolkit(toolkit: Toolkit, server_name: str = None) -> FastMCP:
    """
    Create a FastMCP server from a toolkit.

    Args:
        toolkit: The toolkit to convert
        server_name: Optional name for the MCP server. If not provided, uses toolkit name.

    Returns:
        FastMCP: A configured MCP server with the toolkit's tools
    """
    # Use toolkit name if no server name provided
    server_name = server_name or toolkit.name

    # Create MCP server
    mcp = FastMCP(server_name)

    # Add each tool to the MCP server
    for tool in toolkit.tools:
        # Get the original function's signature
        sig = inspect.signature(tool.fn)

        # Create a wrapper function that preserves the original signature
        @mcp.tool(name=tool.name)
        @wraps(tool.fn)  # This preserves the original function's metadata
        def tool_wrapper(**kwargs):
            # Bind the arguments to the original signature
            bound_args = sig.bind(**kwargs)
            bound_args.apply_defaults()
            return tool.fn(**bound_args.arguments)

        # Update the wrapper's signature to match the original
        tool_wrapper.__signature__ = sig
        tool_wrapper.__doc__ = tool.description

    return mcp
