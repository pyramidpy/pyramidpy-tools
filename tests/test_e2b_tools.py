import pytest
from pyramidpy_tools.e2b.tools import (
    e2b_toolkit,
    create_sandbox,
    close_sandbox,
    execute_command,
    list_sandboxes,
    E2BAuth,
)


@pytest.mark.asyncio
async def test_create_sandbox():
    """Test creating a sandbox environment"""
    result = await create_sandbox()
    assert isinstance(result, dict)
    assert "sandbox_id" in result
    assert "status" in result
    assert result["status"] == "created"


@pytest.mark.asyncio
async def test_create_sandbox_with_template():
    """Test creating a sandbox with a specific template"""
    result = await create_sandbox(template="python")
    assert isinstance(result, dict)
    assert "sandbox_id" in result
    assert "status" in result
    assert result["status"] == "created"


@pytest.mark.asyncio
async def test_close_sandbox():
    """Test closing a sandbox environment"""
    result = await close_sandbox("test-sandbox-id")
    assert isinstance(result, dict)
    assert "sandbox_id" in result
    assert "status" in result
    assert result["status"] == "closed"
    assert result["sandbox_id"] == "test-sandbox-id"


@pytest.mark.asyncio
async def test_execute_command():
    """Test executing a command in a sandbox"""
    result = await execute_command("test-sandbox-id", "ls -la")
    assert isinstance(result, dict)
    assert "sandbox_id" in result
    assert "command" in result
    assert "output" in result
    assert "status" in result
    assert result["status"] == "success"
    assert result["sandbox_id"] == "test-sandbox-id"
    assert result["command"] == "ls -la"


@pytest.mark.asyncio
async def test_list_sandboxes():
    """Test listing sandbox environments"""
    result = await list_sandboxes()
    assert isinstance(result, list)
    assert len(result) > 0
    assert isinstance(result[0], dict)
    assert "sandbox_id" in result[0]
    assert "template" in result[0]
    assert "status" in result[0]


def test_e2b_toolkit_configuration():
    """Test E2B toolkit configuration"""
    assert e2b_toolkit.id == "e2b_toolkit"
    assert e2b_toolkit.name == "E2B Toolkit"
    assert e2b_toolkit.requires_config is True
    assert e2b_toolkit.auth_key == "e2b_auth"
    assert e2b_toolkit.auth_config_schema == E2BAuth

    # Test tools are properly configured
    tool_names = [tool.name for tool in e2b_toolkit.tools]
    assert "create_sandbox" in tool_names
    assert "close_sandbox" in tool_names
    assert "execute_command" in tool_names
    assert "list_sandboxes" in tool_names


def test_e2b_auth_schema():
    """Test E2B authentication schema"""
    auth = E2BAuth(api_key="test-api-key")
    assert auth.api_key == "test-api-key"

    # Test invalid auth
    with pytest.raises(ValueError):
        E2BAuth()
