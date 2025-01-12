from typing import Any, List, Literal, TypeVar

from controlflow.tools.tools import Tool
from pydantic import BaseModel, Field

BaseType = TypeVar("BaseType", bound=BaseModel)


class Toolkit(BaseModel):
    id: str = Field(description="App ID of the toolkit", default="")
    name: str = Field(description="Name of the toolkit", default="")
    description: str = Field(description="Description of the toolkit", default="")
    default: bool = Field(
        description="Default toolkits available to all agents", default=True
    )
    tools: List[Tool] | None = Field(
        description="List of tools in the toolkit", default=None
    )
    requires_config: bool = Field(
        description="Whether the toolkit requires a config", default=False
    )
    active_tools: List[str] | None | Literal["all"] = Field(
        description="Active tools for the toolkit", default="all"
    )
    auth_key: str | None = Field(
        description="Authentication key for the toolkit from context", default=None
    )
    auth_config: Any | dict | None = Field(
        description="Authentication config for the toolkit", default=None, exclude=True
    )
    auth_config_schema: Any | dict | None = Field(
        description="Authentication config for the toolkit. Should be a Pydantic model.", default=None, exclude=True
    )
    category: Literal["channel", "tool", "other"] = Field(
        description="Category of the toolkit", default="other"
    )
    is_app_default: bool = Field(
        description="Whether the toolkit is an app default", default=False
    )

    def to_tool_list(self) -> List[Tool]:
        tools = []
        if self.active_tools not in [None, "all"]:
            all_tools = self.tools
            for tool in all_tools:
                if tool.name in self.active_tools:
                    tools.append(tool)
        else:
            tools = self.tools
        return tools

    def add_tool(self, tool_id: str):
        tool_ids = [t.name for t in self.tools]
        if tool_id in tool_ids:
            self.active_tools.append(tool_id)
        else:
            raise ValueError(f"Tool {tool_id} not found in toolkit {self.name}")

    def remove_tool(self, tool_id: str):
        tool_ids = [t.name for t in self.tools]
        if tool_id in tool_ids:
            self.active_tools.remove(tool_id)
        else:
            raise ValueError(f"Tool {tool_id} not found in toolkit {self.name}")

    @classmethod
    def create_toolkit(
        cls,
        id: str,
        tools: List[Tool],
        name: str,
        description: str = "",
        requires_config: bool = False,
        auth_key: str | None = None,
        auth_config_schema: type[BaseModel] | None = None,
        active_tools: List[str] | None | Literal["all"] = "all",
        is_channel: bool = False,
        **kwargs,
    ):
        return cls(
            id=id,
            name=name,
            description=description,
            tools=tools,
            requires_config=requires_config,
            auth_key=auth_key,
            auth_config_schema=auth_config_schema,
            active_tools=active_tools,
            is_channel=is_channel,
            **kwargs,
        )

    # run a tool in a toolkit
    def run_tool(self, tool_id: str, input: dict):
        tool = next((t for t in self.tools if t.name == tool_id), None)
        if not tool:
            raise ValueError(f"Tool {tool_id} not found in toolkit {self.name}")
        return tool.run(input)

    def run_tool_async(self, tool_id: str, input: dict):
        tool = next((t for t in self.tools if t.name == tool_id), None)
        if not tool:
            raise ValueError(f"Tool {tool_id} not found in toolkit {self.name}")
        return tool.run_async(input)
