"""
E2B tools for code execution and display
"""

import traceback
from typing import List

from pydantic import Field
from controlflow.tools.tools import tool
from controlflow.flows.flow import get_flow
from e2b_code_interpreter import Sandbox
from loguru import logger
from pyramidpy_tools.toolkit import Toolkit
from pyramidpy_tools.utilities.auth import get_auth_from_context
from pyramidpy_tools.settings import settings
from .schemas import CodeBlock, CodeResult, E2BConfig
from .utils import handle_execution_result


AUTH_KEY = "e2b_api_key"


def get_e2b_api_key():
    flow = get_flow()
    auth = get_auth_from_context(flow.context, AUTH_KEY)
    if auth:
        return E2BConfig(**auth).api_key
    else:
        return settings.tool_provider.e2b_api_key


@tool(
    name="code_block",
    description="Display code in a custom component",
    include_return_description=False,
)
def code_block(code: str, language: str = "python", **kwargs) -> CodeBlock:
    """
    Use this tool to display any code to the user.

    Args:
        code: The code to display
        language: The programming language of the code (default: python)
        **kwargs: Additional keyword arguments

    Returns:
        CodeBlock: A formatted code block for display
    """
    return CodeBlock(code=code, language=language, highlighted_sections=[])


@tool(
    name="code_interpreter",
    description="Execute Python code in a sandboxed environment",
    include_return_description=False,
)
async def code_interpreter(
    code: str,
    timeout: int = Field(
        default=3000, description="Timeout for code execution in milliseconds"
    ),
    download_files: List[str] = [],
    **kwargs,
) -> CodeResult:
    """
    Execute code in a sandboxed jupyter notebook environment.

    Args:
        code: The code to execute
        download_files: List of file paths to download from the sandbox (must be relative to the 'mnt' directory)
        **kwargs: Additional keyword arguments including context

    Returns:
        CodeResult: The result of code execution

    Notes:
        - If you explicitly create any files, specify them in the download_files list
        - Use the 'mnt' directory for file paths
        - Files with long urls will be automatically shown to the user
        - You do not need to specify the return
    """

    api_key = get_e2b_api_key()

    try:
        sandbox = Sandbox(
            api_key=api_key,
            timeout=timeout,
        )

        logger.info(
            f"\n{'='*50}\n> Running following AI-generated code:\n{code}\n{'='*50}"
        )

        execution = sandbox.run_code(code)

        if execution.error:
            return CodeResult(output="", files=[], error=str(execution.error))

        files = []
        data_sources = []
        for idx, result in enumerate(execution.results):
            _files, _data_sources = await handle_execution_result(result)
            files.extend(_files)
            data_sources.extend(_data_sources)

        return CodeResult(
            logs=str(execution.logs),
            output=str(execution.results),
            files=files,
            data_sources=data_sources,
            error="",
        )
    except Exception as e:
        traceback.print_exc()
        return CodeResult(output="", files=[], error=str(e))


# Create the toolkits
code_ix = Toolkit.create_toolkit(
    id="code_interpreter",
    name="Code Interpreter",
    icon="Terminal",
    description="Tools for executing code in an isolated environment",
    tools=[code_interpreter, code_block],
    categories=["code_interpreter"],
    requires_config=True,
    auth_key=AUTH_KEY,
    auth_config_schema=E2BConfig,
)
