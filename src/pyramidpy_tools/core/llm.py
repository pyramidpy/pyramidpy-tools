# TODO: Add support for providers and improve loading
from enum import Enum

from controlflow.llm.models import get_model
from langchain_anthropic import ChatAnthropic
from langchain_community.chat_models import ChatLiteLLM
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain_together import Together
from loguru import logger

from pyramidpy_tools.settings import settings


class SupportedProviders(Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"
    ollama = "ollama"
    azure = "azure"
    together = "together"
    deepseek = "deepseek"


class SupportedModels(Enum):
    deepseek_chat = "deepseek/deepseek-chat"
    deepseek_reasoner = "deepseek/deepseek-reasoner"
    claude_3_5_sonnet = "anthropic/claude-3-5-sonnet-20241022"
    claude_3_opus = "anthropic/claude-3-opus-20240229"
    gemini_1_5_flash = "google/gemini-1.5-flash-latest"
    gpt_4o_mini = "openai/gpt-4o-mini"
    gpt_4o = "openai/gpt-4o"
    gpt_4o_turbo = "openai/gpt-4o-turbo"
    o1_mini = "openai/o1-mini"
    o1 = "openai/o1"


def get_llm(model_id: str | None = "openai/gpt-4o-mini"):
    deep_seek_llm = ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=settings.llm.deepseek_api_key,
        openai_api_base="https://api.deepseek.com",
        streaming=True,
    )

    anthropic_llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241020",
        anthropic_api_key=settings.llm.anthropic_api_key,
    )

    gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        google_api_key=settings.llm.google_api_key,
    )

    if settings.llm.together_api_key:
        together_llm = Together(
            model="meta-llama/llama-3.1-8b-instruct",
            together_api_key=settings.llm.together_api_key,
        )

    deepseek_reasoner_llm = ChatLiteLLM(
        model="deepseek/deepseek-reasoner",
        api_key=settings.llm.deepseek_api_key,
        api_base="https://api.deepseek.com",
    )

    match model_id:
        case "deepseek/deepseek-v3":
            return deep_seek_llm
        case "anthropic/claude-3-5-sonnet-20241022":
            return anthropic_llm
        case "google/gemini-1.5-flash-latest":
            return gemini_llm
        case "meta-llama/llama-3.1-8b-instruct":
            return together_llm
        case "deepseek/deepseek-reasoner":
            return deepseek_reasoner_llm
        case _:
            logger.warning(f"Model {model_id} not found, using default model")
            return get_model("openai/gpt-4o-mini")
