from typing import List

from controlflow.tools.tools import Tool

from pyramidpy_tools.toolkit import Toolkit

from .apify.tools import apify_toolkit
from .dex_screener.tools import dex_screener_toolkit
from .discord_bot.tools import discord_toolkit
from .file_system.tools import file_system_toolkit
from .github.tools import github_toolkit
from .jina.tools import jina_toolkit
from .kb.tools import knowledge_base_toolkit
from .slack.tools import slack_toolkit
from .tavily_search.tools import tavily_toolkit
from .telegram.tools import telegram_toolkit
from .twitter_user.tools import twitter_toolkit


def get_tools(toolkits: List[Toolkit]) -> List[Tool]:
    tools = []
    for toolkit in toolkits:
        tools.extend(toolkit.tools)
    return tools


def get_all_tools():
    return get_tools(
        [
            twitter_toolkit,
            dex_screener_toolkit,
            file_system_toolkit,
            knowledge_base_toolkit,
            tavily_toolkit,
            telegram_toolkit,
            discord_toolkit,
            github_toolkit,
            slack_toolkit,
            apify_toolkit,
            jina_toolkit,
            apify_toolkit,
            telegram_toolkit,
        ]
    )


def get_all_toolkits():
    return [
        twitter_toolkit,
        discord_toolkit,
        dex_screener_toolkit,
        file_system_toolkit,
        knowledge_base_toolkit,
        github_toolkit,
        slack_toolkit,
        tavily_toolkit,
        dex_screener_toolkit,
        jina_toolkit,
        file_system_toolkit,
        knowledge_base_toolkit,
        apify_toolkit,
        telegram_toolkit,
    ]


def get_tools_from_toolkit_ids(toolkit_ids: List[str]) -> List[Tool]:
    toolkits = [toolkit for toolkit in get_all_toolkits() if toolkit.id in toolkit_ids]
    return get_tools(toolkits)


__all__ = [
    "twitter_toolkit",
    "dex_screener_toolkit",
    "file_system_toolkit",
    "knowledge_base_toolkit",
    "github_toolkit",
    "slack_toolkit",
    "jina_toolkit",
    "apify_toolkit",
    "telegram_toolkit",
    "discord_toolkit",
]
