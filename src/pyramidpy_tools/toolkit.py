from typing import Any, List, Literal, TypeVar

from controlflow.tools.tools import Tool
from pydantic import BaseModel, Field, field_validator

BaseType = TypeVar("BaseType", bound=BaseModel)


class Toolkit(BaseModel):
    # TODO clean up and remove duplicates and unused.
    id: str = Field(description="DB ID of the toolkit", default="")
    name: str = Field(description="Name of the toolkit", default="")
    description: str = Field(description="Description of the toolkit", default="")
    default: bool = Field(
        description="Default toolkits available to all agents", default=True
    )
    tools: List[Tool] | None = Field(
        description="List of tools in the toolkit", default=[]
    )
    requires_config: bool = Field(
        description="Whether the toolkit requires a config", default=False
    )
    auth_config: dict | None = Field(
        description="Config for the toolkit", default=None
    )
    active_tools: List[str] | None | Literal["all"] = Field(
        description="Active tools for the toolkit", default="all"
    )
    auth_key: str | None = Field(
        description="Authentication key for the toolkit from context", default=None
    )
    auth_config_schema: Any | dict | None = Field(
        description="Authentication config for the toolkit", default=None, exclude=True
    )
    is_channel: bool = Field(
        description="Whether the toolkit is a channel", default=False
    )
    is_app_default: bool = Field(
        description="Whether the toolkit is an app default", default=False
    )
    custom_name: str | None = Field(
        description="User defined name for the toolkit", default=None
    )
    custom_description: str | None = Field(
        description="User defined description for the toolkit", default=None
    )
    custom_instructions: str | None = Field(
        description="User defined instructions for the toolkit", default=None
    )

    config: dict | None = Field(
        description="Configuration for the toolkit.", default=None
    )
    config_schema: dict | None | str = Field(
        description="Schema for the toolkit configuration", default=None
    )
    tools_schema: dict | list | None = Field(
        description="Schema for the tools in the toolkit", default=None
    )

    db_id: str | None = Field(
        description="The id of the toolkit in the database", default=None
    )
    access_list: list[str] | None = Field(
        description="List of users & Agents who have access to the toolkit", default=None
    )
    setup_complete: bool = Field(
        description="Set to true if toolkit has configuration", default=False
    )

    @field_validator("tools", mode="after")
    def validate_tools(cls, v):
        if v is None:
            return []
        return v

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
        # TODO should be run in a flow
        
        tool = next((t for t in self.tools if t.name == tool_id), None)
        if not tool:
            raise ValueError(f"Tool {tool_id} not found in toolkit {self.name}")
        return tool.run(input)

    def run_tool_async(self, tool_id: str, input: dict):
        # TODO should be run in a flow
        tool = next((t for t in self.tools if t.name == tool_id), None)
        if not tool:
            raise ValueError(f"Tool {tool_id} not found in toolkit {self.name}")
        return tool.run_async(input)
