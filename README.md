# Welcome to PyramidPy Tools

Collection of tools for PyramidPy.

## Installation

```bash
pip install pyramidpy-tools
```

## Usage

Available toolkits:
```python
from pyramidpy_tools.tools import get_all_toolkits
```

## Using a toolkit

### Dex Screener

```python
from pyramidpy_tools.dex_screener.tools import dex_screener_toolkit
```

### Inject Context Inflows

```python
Allows tools to be configurable at runtime.

from controlflow.flows.flow import get_flow
def get_github_api() -> GitHubAPI:
    """Get GitHub API instance with token from context if available"""
    flow = get_flow()
    if flow and flow.context:
        token = flow.context.get("github_token")
        if token:
            return GitHubAPI(token=token)
    return GitHubAPI()
```
