# PyramidPy Tools 🛠️

[![Tests](https://github.com/pyramidpy/pyramidpy-tools/actions/workflows/test.yml/badge.svg)](https://github.com/pyramidpy/pyramidpy-tools/actions/workflows/test.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive collection of curated toolkits for the PyramidPy project.
This repository provides ready-to-use tools and integrations to enhance your AI agent capabilities.

## 🌟 Features

- Over 50+ tools across 5 categories
- MCP server support
- Tools include:
  - 🔍 **Tavily Search**: Integration with Tavily's AI-powered search API
  - 🤖 **Apify Tools**: Web scraping and automation capabilities
  - 💬 **Telegram Tools**: Telegram bot integration utilities
  - 📊 **DEX Screener**: Tools for cryptocurrency DEX analysis
  - 🎯 **Jina Tools**: Neural search and indexing capabilities
  - 📈 **Twitter Tools**: Twitter bot integration utilities

And many more

## 🚀 Installation

```bash
uv add pyramidpy-tools

# or with pip
pip install pyramidpy-tools
```

## 🛠️ Quick Start

```python
from pyramidpy_tools import PyramidToolkit

# Initialize the toolkit
toolkit = PyramidToolkit()

# Use specific tools
tavily_tool = toolkit.get_tool("tavily_search")
telegram_tool = toolkit.get_tool("telegram")
```

## 🔧 Development

1. Clone the repository:
```bash
git clone https://github.com/pyramidpy/pyramidpy-tools.git
cd pyramidpy-tools
```

2. Install dependencies:
```bash
uv sync --all-extras
```

3. Run tests:
```bash
pytest tests/
```

## MCP Server

You can find example of how to use the MCP server in the [examples](examples) folder.

create a file called `twitter_mcp.py` and add the following code:

```python
from pyramidpy_tools.toolkit_to_mcp import create_mcp_from_toolkit
from pyramidpy_tools.twitter_user.tools import twitter_toolkit

mcp = create_mcp_from_toolkit(twitter_toolkit, "Twitter MCP Server")
```

Start the MCP server:

```bash
fastmcp dev twitter_mcp.py

```



## 🤝 Contributing

We love your input! We want to make contributing to PyramidPy Tools as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features

We are working on a tooling (powered by agents of course) to help you contribute to this project.

Check out our [Contributing Guide](CONTRIBUTING.md) for ways to get started.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Related Projects

- [PyramidPy](https://github.com/pyramidpy/PyramidPy) - Main PyramidPy project
