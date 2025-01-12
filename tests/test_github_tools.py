from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from controlflow.tools.tools import Tool

from pyramidpy_tools.github.schemas import FileOperation
from pyramidpy_tools.github.tools import (
    get_github_api,
    github_toolkit,
)


def test_get_github_api_with_token():
    with patch(
        "pyramidpy_tools.settings.settings.tool_provider.github_token.get_secret_value",
        return_value="default-token",
    ):
        with patch("controlflow.flows.flow.get_flow") as mock_get_flow:
            mock_flow = MagicMock()
            mock_flow.context = {"github_token": "test-token"}
            mock_get_flow.return_value = mock_flow

            api = get_github_api()
            assert api.token == "test-token"


def test_get_github_api_without_token():
    with patch(
        "pyramidpy_tools.settings.settings.tool_provider.github_token.get_secret_value",
        return_value="default-token",
    ):
        with patch("controlflow.flows.flow.get_flow") as mock_get_flow:
            mock_get_flow.return_value = None

            api = get_github_api()
            assert api.token == "default-token"


def test_tools_are_properly_configured():
    """Test that all tools are properly configured in the toolkit"""
    assert isinstance(github_toolkit.tools[0], Tool)
    for tool in github_toolkit.tools:
        assert isinstance(tool, Tool)
        assert tool.name.startswith("github_")
        assert tool.description
        assert callable(tool.fn)


@pytest.fixture
def mock_api():
    with patch("pyramidpy_tools.tools.github.tools.get_github_api") as mock:
        mock_instance = AsyncMock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.mark.asyncio
async def test_github_create_issue(mock_api):
    expected_response = {
        "number": 1,
        "title": "Test Issue",
        "body": "Test Body",
        "html_url": "https://github.com/test/test/issues/1",
    }
    mock_api.create_issue.return_value = expected_response

    create_issue_tool = next(
        t for t in github_toolkit.tools if t.name == "github_create_issue"
    )
    result = await create_issue_tool.run_async(
        {"owner": "test", "repo": "test", "title": "Test Issue", "body": "Test Body"}
    )

    assert result["number"] == 1
    assert result["title"] == "Test Issue"
    mock_api.create_issue.assert_called_once_with(
        owner="test", repo="test", title="Test Issue", body="Test Body"
    )


@pytest.mark.asyncio
async def test_github_create_pull_request(mock_api):
    expected_response = {
        "number": 1,
        "title": "Test PR",
        "html_url": "https://github.com/test/test/pull/1",
    }
    mock_api.create_pull_request.return_value = expected_response

    create_pr_tool = next(
        t for t in github_toolkit.tools if t.name == "github_create_pull_request"
    )
    result = await create_pr_tool.run_async(
        {
            "owner": "test",
            "repo": "test",
            "title": "Test PR",
            "head": "feature",
            "base": "main",
        }
    )

    assert result["number"] == 1
    assert result["title"] == "Test PR"
    mock_api.create_pull_request.assert_called_once_with(
        owner="test", repo="test", title="Test PR", head="feature", base="main"
    )


@pytest.mark.asyncio
async def test_github_search_repositories(mock_api):
    expected_response = {
        "total_count": 1,
        "items": [
            {
                "name": "test-repo",
                "full_name": "test/test-repo",
                "html_url": "https://github.com/test/test-repo",
            }
        ],
    }
    mock_api.search_repositories.return_value = expected_response

    search_repos_tool = next(
        t for t in github_toolkit.tools if t.name == "github_search_repositories"
    )
    result = await search_repos_tool.run_async({"query": "test"})

    assert result["total_count"] == 1
    assert len(result["items"]) == 1
    mock_api.search_repositories.assert_called_once_with(query="test")


@pytest.mark.asyncio
async def test_github_create_repository(mock_api):
    expected_response = {
        "name": "test-repo",
        "full_name": "test/test-repo",
        "private": False,
        "html_url": "https://github.com/test/test-repo",
    }
    mock_api.create_repository.return_value = expected_response

    create_repo_tool = next(
        t for t in github_toolkit.tools if t.name == "github_create_repository"
    )
    result = await create_repo_tool.run_async(
        {"name": "test-repo", "description": "Test repository", "private": False}
    )

    assert result["name"] == "test-repo"
    assert result["full_name"] == "test/test-repo"
    mock_api.create_repository.assert_called_once_with(
        name="test-repo", description="Test repository", private=False
    )


@pytest.mark.asyncio
async def test_github_get_file_contents(mock_api):
    expected_response = {
        "type": "file",
        "content": "dGVzdCBjb250ZW50",  # base64 encoded "test content"
        "encoding": "base64",
    }
    mock_api.get_file_contents.return_value = expected_response

    get_contents_tool = next(
        t for t in github_toolkit.tools if t.name == "github_get_file_contents"
    )
    result = await get_contents_tool.run_async(
        {"owner": "test", "repo": "test", "path": "test.txt"}
    )

    assert result["type"] == "file"
    assert result["content"] == "dGVzdCBjb250ZW50"
    mock_api.get_file_contents.assert_called_once_with(
        owner="test", repo="test", path="test.txt"
    )


@pytest.mark.asyncio
async def test_github_list_issues(mock_api):
    expected_response = [{"number": 1, "title": "Test Issue", "state": "open"}]
    mock_api.list_issues.return_value = expected_response

    list_issues_tool = next(
        t for t in github_toolkit.tools if t.name == "github_list_issues"
    )
    result = await list_issues_tool.run_async(
        {"owner": "test", "repo": "test", "state": "open"}
    )

    assert len(result) == 1
    assert result[0]["number"] == 1
    mock_api.list_issues.assert_called_once_with(
        owner="test", repo="test", state="open"
    )


@pytest.mark.asyncio
async def test_github_create_branch(mock_api):
    mock_api.get_default_branch_sha.return_value = "test-sha"
    expected_response = {"ref": "refs/heads/feature", "object": {"sha": "test-sha"}}
    mock_api.create_branch.return_value = expected_response

    create_branch_tool = next(
        t for t in github_toolkit.tools if t.name == "github_create_branch"
    )
    result = await create_branch_tool.run_async(
        {"owner": "test", "repo": "test", "branch": "feature"}
    )

    assert result["ref"] == "refs/heads/feature"
    assert result["object"]["sha"] == "test-sha"
    mock_api.create_branch.assert_called_once()


@pytest.mark.asyncio
async def test_github_create_or_update_file(mock_api):
    expected_response = {"content": {"path": "test.txt", "sha": "new-sha"}}
    mock_api.create_or_update_file.return_value = expected_response

    update_file_tool = next(
        t for t in github_toolkit.tools if t.name == "github_create_or_update_file"
    )
    result = await update_file_tool.run_async(
        {
            "owner": "test",
            "repo": "test",
            "path": "test.txt",
            "content": "test content",
            "message": "test commit",
            "branch": "main",
        }
    )

    assert result["content"]["path"] == "test.txt"
    assert result["content"]["sha"] == "new-sha"
    mock_api.create_or_update_file.assert_called_once_with(
        owner="test",
        repo="test",
        path="test.txt",
        content="test content",
        message="test commit",
        branch="main",
    )


@pytest.mark.asyncio
async def test_github_push_files(mock_api):
    expected_response = {
        "sha": "new-commit-sha",
        "url": "https://api.github.com/repos/test/test/git/commits/new-commit-sha",
    }
    mock_api.push_files.return_value = expected_response

    files = [
        FileOperation(path="test1.txt", content="content1", operation="create"),
        FileOperation(path="test2.txt", content="content2", operation="update"),
    ]

    push_files_tool = next(
        t for t in github_toolkit.tools if t.name == "github_push_files"
    )
    result = await push_files_tool.run_async(
        {
            "owner": "test",
            "repo": "test",
            "branch": "main",
            "files": files,
            "message": "test commit",
        }
    )

    assert result["sha"] == "new-commit-sha"
    mock_api.push_files.assert_called_once_with(
        owner="test", repo="test", branch="main", files=files, message="test commit"
    )


@pytest.mark.asyncio
async def test_github_list_commits(mock_api):
    expected_response = [{"sha": "test-sha", "commit": {"message": "test commit"}}]
    mock_api.list_commits.return_value = expected_response

    list_commits_tool = next(
        t for t in github_toolkit.tools if t.name == "github_list_commits"
    )
    result = await list_commits_tool.run_async({"owner": "test", "repo": "test"})

    assert len(result) == 1
    assert result[0]["sha"] == "test-sha"
    mock_api.list_commits.assert_called_once_with(owner="test", repo="test")


@pytest.mark.asyncio
async def test_github_update_issue(mock_api):
    expected_response = {
        "number": 1,
        "title": "Updated Issue",
        "state": "closed",
    }
    mock_api.update_issue.return_value = expected_response

    update_issue_tool = next(
        t for t in github_toolkit.tools if t.name == "github_update_issue"
    )
    result = await update_issue_tool.run_async(
        {
            "owner": "test",
            "repo": "test",
            "issue_number": 1,
            "title": "Updated Issue",
            "state": "closed",
        }
    )

    assert result["title"] == "Updated Issue"
    assert result["state"] == "closed"
    mock_api.update_issue.assert_called_once_with(
        owner="test", repo="test", issue_number=1, title="Updated Issue", state="closed"
    )


@pytest.mark.asyncio
async def test_github_add_issue_comment(mock_api):
    expected_response = {"id": 1, "body": "Test comment"}
    mock_api.add_issue_comment.return_value = expected_response

    add_comment_tool = next(
        t for t in github_toolkit.tools if t.name == "github_add_issue_comment"
    )
    result = await add_comment_tool.run_async(
        {"owner": "test", "repo": "test", "issue_number": 1, "body": "Test comment"}
    )

    assert result["body"] == "Test comment"
    mock_api.add_issue_comment.assert_called_once_with(
        owner="test", repo="test", issue_number=1, body="Test comment"
    )
