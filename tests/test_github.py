from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from github.Branch import Branch
from github.Commit import Commit
from github.ContentFile import ContentFile
from github.GitRef import GitRef
from github.Issue import Issue
from github.IssueComment import IssueComment
from github.PullRequest import PullRequest
from github.Repository import Repository

from pyramidpy_tools.github.base import GitHubAPI
from pyramidpy_tools.github.schemas import (
    CreateBranchOptions,
    CreateIssueOptions,
    CreatePullRequestOptions,
    CreateRepositoryOptions,
    FileOperation,
    GitHubAuth,
)
from pyramidpy_tools.github.tools import (
    get_github_api,
    github_add_collaborator,
    github_add_issue_comment,
    github_add_labels,
    github_add_pull_request_comment,
    github_add_pull_request_review,
    github_compare_commits,
    github_create_branch,
    github_create_issue,
    github_create_label,
    github_create_or_update_file,
    github_create_pull_request,
    github_create_release,
    github_create_repository,
    github_delete_branch,
    github_delete_file,
    github_get_commit,
    github_get_default_branch,
    github_get_file_contents,
    github_get_repository_permissions,
    github_list_branches,
    github_list_collaborators,
    github_list_commits,
    github_list_directory_contents,
    github_list_issue_comments,
    github_list_issues,
    github_list_labels,
    github_list_pull_request_files,
    github_list_pull_requests,
    github_list_releases,
    github_merge_pull_request,
    github_push_files,
    github_remove_collaborator,
    github_remove_labels,
    github_search_repositories,
    github_set_default_branch,
    github_update_issue,
    github_update_pull_request,
)


@pytest.fixture
def mock_github_api():
    with patch("pyramidpy_tools.github.tools.GitHubAPI") as mock_api_class:
        mock_api = MagicMock(spec=GitHubAPI)
        mock_api_class.return_value = mock_api
        # Mock the auth property
        mock_api.auth = GitHubAuth(token="test-token")
        # Add get_branch method to mock
        mock_api.get_branch = AsyncMock()
        yield mock_api


def test_get_github_api_with_token():
    auth_data = {"auth": {"github_token": GitHubAuth(token="test-token").model_dump()}}

    with patch("pyramidpy_tools.github.tools.get_flow") as mock_get_flow:
        # Setup mock flow with proper context structure
        mock_flow = MagicMock()
        mock_flow.context = auth_data
        mock_get_flow.return_value = mock_flow

        api = get_github_api()
        assert isinstance(api, GitHubAPI)
        assert api.auth.token == "test-token"


def test_get_github_api_without_token():
    with patch("pyramidpy_tools.github.tools.get_flow") as mock_get_flow:
        mock_get_flow.return_value = None
        with patch("pyramidpy_tools.github.tools.settings") as mock_settings:
            mock_settings.tool_provider.github_token = "default-token"
            api = get_github_api()
            assert isinstance(api, GitHubAPI)
            assert api.auth.token == "default-token"


@pytest.mark.asyncio
async def test_github_create_issue(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_issue = MagicMock(spec=Issue)
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        mock_issue.body = "Test Body"
        mock_github_api.create_issue.return_value = mock_issue

        result = await github_create_issue.fn(
            owner="test-owner", repo="test-repo", title="Test Issue", body="Test Body"
        )

        assert result.number == 1
        assert result.title == "Test Issue"
        assert mock_github_api.create_issue.call_count == 1
        mock_github_api.create_issue.assert_called_once_with(
            "test-owner",
            "test-repo",
            CreateIssueOptions(title="Test Issue", body="Test Body"),
        )


@pytest.mark.asyncio
async def test_github_create_pull_request(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_pr = MagicMock(spec=PullRequest)
        mock_pr.number = 1
        mock_pr.title = "Test PR"
        mock_pr.body = "Test Body"
        mock_pr.html_url = "https://github.com/test/test/pull/1"
        mock_github_api.create_pull_request.return_value = mock_pr

        result = await github_create_pull_request.fn(
            owner="test-owner",
            repo="test-repo",
            title="Test PR",
            body="Test Body",
            head="feature",
            base="main",
        )

        assert result.number == 1
        assert result.title == "Test PR"
        assert mock_github_api.create_pull_request.call_count == 1
        mock_github_api.create_pull_request.assert_called_once_with(
            "test-owner",
            "test-repo",
            CreatePullRequestOptions(
                title="Test PR", body="Test Body", head="feature", base="main"
            ),
        )


@pytest.mark.asyncio
async def test_github_search_repositories(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_repo = MagicMock(spec=Repository)
        mock_repo.name = "test-repo"
        mock_repo.full_name = "test/test-repo"
        mock_github_api.search_repositories.return_value = [mock_repo]

        result = await github_search_repositories.fn(query="test")

        assert len(result) == 1
        assert result[0].name == "test-repo"
        assert mock_github_api.search_repositories.call_count == 1
        mock_github_api.search_repositories.assert_called_once_with("test", 1, 30)


@pytest.mark.asyncio
async def test_github_create_repository(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_repo = MagicMock(spec=Repository)
        mock_repo.name = "test-repo"
        mock_repo.full_name = "test/test-repo"
        mock_repo.private = True
        mock_github_api.create_repository.return_value = mock_repo

        result = await github_create_repository.fn(
            name="test-repo", private=True, description="Test description"
        )

        assert result.name == "test-repo"
        assert result.private is True
        assert mock_github_api.create_repository.call_count == 1
        mock_github_api.create_repository.assert_called_once_with(
            CreateRepositoryOptions(
                name="test-repo", private=True, description="Test description"
            )
        )


@pytest.mark.asyncio
async def test_github_get_file_contents(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_content = MagicMock(spec=ContentFile)
        mock_content.content = "test content"
        mock_content.sha = "test-sha"
        mock_github_api.get_file_contents.return_value = mock_content

        result = await github_get_file_contents.fn(
            owner="test-owner", repo="test-repo", path="test/path.txt"
        )

        assert result.content == "test content"
        assert mock_github_api.get_file_contents.call_count == 1
        mock_github_api.get_file_contents.assert_called_once_with(
            "test-owner", "test-repo", "test/path.txt", None
        )


@pytest.mark.asyncio
async def test_github_list_issues(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_issue1 = MagicMock(spec=Issue)
        mock_issue1.number = 1
        mock_issue1.title = "Issue 1"
        mock_issue2 = MagicMock(spec=Issue)
        mock_issue2.number = 2
        mock_issue2.title = "Issue 2"
        mock_github_api.list_issues.return_value = [mock_issue1, mock_issue2]

        result = await github_list_issues.fn(
            owner="test-owner", repo="test-repo", state="open"
        )

        assert len(result) == 2
        assert result[0].title == "Issue 1"
        assert mock_github_api.list_issues.call_count == 1
        mock_github_api.list_issues.assert_called_once_with(
            "test-owner",
            "test-repo",
            "open",
            None,  # labels
            None,  # sort
            None,  # direction
            None,  # since
            None,  # page
            None,  # per_page
        )


@pytest.mark.asyncio
async def test_github_create_branch(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        # Mock the branch reference for create_branch result
        mock_ref = MagicMock(spec=GitRef)
        mock_ref.ref = "refs/heads/feature"
        mock_ref.object.sha = "test-sha"
        mock_github_api.create_branch.return_value = mock_ref

        # Mock get_branch to return a proper Branch object
        mock_commit = MagicMock()
        mock_commit.sha = "test-sha"  # This needs to be a string
        mock_source_branch = MagicMock(spec=Branch)
        mock_source_branch.commit = mock_commit
        mock_github_api.get_branch = AsyncMock(return_value=mock_source_branch)

        result = await github_create_branch.fn(
            owner="test-owner", repo="test-repo", branch="feature", from_branch="main"
        )

        assert result.ref == "refs/heads/feature"
        # Verify get_branch was called with correct parameters
        mock_github_api.get_branch.assert_awaited_once_with(
            "test-owner", "test-repo", "main"
        )
        # Verify create_branch was called with correct parameters
        mock_github_api.create_branch.assert_called_once_with(
            "test-owner",
            "test-repo",
            CreateBranchOptions(ref="feature", sha="test-sha"),
        )


@pytest.mark.asyncio
async def test_github_create_or_update_file(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_content = MagicMock(spec=ContentFile)
        mock_content.sha = "new-sha"
        mock_commit = MagicMock(spec=Commit)
        mock_commit.sha = "commit-sha"
        mock_github_api.create_or_update_file.return_value = {
            "content": mock_content,
            "commit": mock_commit,
        }

        result = await github_create_or_update_file.fn(
            owner="test-owner",
            repo="test-repo",
            path="test/file.txt",
            message="Test commit",
            content="Test content",
            branch="main",
        )

        assert result["content"].sha == "new-sha"
        assert mock_github_api.create_or_update_file.call_count == 1
        mock_github_api.create_or_update_file.assert_called_once_with(
            "test-owner",
            "test-repo",
            "test/file.txt",
            "Test content",
            "Test commit",
            "main",
            None,
        )


@pytest.mark.asyncio
async def test_github_push_files(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_ref = MagicMock(spec=GitRef)
        mock_ref.ref = "refs/heads/main"
        mock_ref.object.sha = "commit-sha"
        mock_github_api.push_files.return_value = mock_ref

        files = [
            FileOperation(
                path="test/file.txt", content="Test content", operation="create"
            )
        ]

        result = await github_push_files.fn(
            owner="test-owner",
            repo="test-repo",
            branch="main",
            message="Test commit",
            files=files,
        )

        assert result.ref == "refs/heads/main"
        assert mock_github_api.push_files.call_count == 1
        mock_github_api.push_files.assert_called_once_with(
            "test-owner", "test-repo", "main", files, "Test commit"
        )


@pytest.mark.asyncio
async def test_github_list_commits(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_commit1 = MagicMock(spec=Commit)
        mock_commit1.sha = "commit-1"
        mock_commit1.commit.message = "Test commit 1"
        mock_commit2 = MagicMock(spec=Commit)
        mock_commit2.sha = "commit-2"
        mock_commit2.commit.message = "Test commit 2"
        mock_github_api.list_commits.return_value = [mock_commit1, mock_commit2]

        result = await github_list_commits.fn(owner="test-owner", repo="test-repo")

        assert len(result) == 2
        assert result[0].sha == "commit-1"
        assert mock_github_api.list_commits.call_count == 1
        mock_github_api.list_commits.assert_called_once_with(
            "test-owner",
            "test-repo",
            1,  # page
            30,  # per_page
            None,  # sha
        )


@pytest.mark.asyncio
async def test_github_update_issue(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_issue = MagicMock(spec=Issue)
        mock_issue.number = 1
        mock_issue.title = "Updated Issue"
        mock_issue.state = "closed"
        mock_github_api.update_issue.return_value = mock_issue

        result = await github_update_issue.fn(
            owner="test-owner",
            repo="test-repo",
            issue_number=1,
            title="Updated Issue",
            state="closed",
        )

        assert result.title == "Updated Issue"
        assert result.state == "closed"
        assert mock_github_api.update_issue.call_count == 1
        mock_github_api.update_issue.assert_called_once_with(
            "test-owner",
            "test-repo",
            1,
            "Updated Issue",  # title
            None,  # body
            "closed",  # state
            None,  # labels
            None,  # assignees
            None,  # milestone
        )


@pytest.mark.asyncio
async def test_github_add_issue_comment(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_comment = MagicMock(spec=IssueComment)
        mock_comment.id = 1
        mock_comment.body = "Test comment"
        mock_github_api.add_issue_comment.return_value = mock_comment

        result = await github_add_issue_comment.fn(
            owner="test-owner", repo="test-repo", issue_number=1, body="Test comment"
        )

        assert result.body == "Test comment"
        assert mock_github_api.add_issue_comment.call_count == 1
        mock_github_api.add_issue_comment.assert_called_once_with(
            "test-owner",
            "test-repo",
            1,
            "Test comment",  # body
        )


@pytest.mark.asyncio
async def test_github_list_branches(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_branch1 = MagicMock()
        mock_branch1.name = "main"
        mock_branch2 = MagicMock()
        mock_branch2.name = "feature"
        mock_github_api.list_branches.return_value = [mock_branch1, mock_branch2]

        result = await github_list_branches.fn(
            owner="test-owner", repo="test-repo", page=1, per_page=30
        )

        assert len(result) == 2
        assert result[0].name == "main"
        assert result[1].name == "feature"
        mock_github_api.list_branches.assert_called_once_with(
            "test-owner", "test-repo", 1, 30
        )


@pytest.mark.asyncio
async def test_github_delete_branch(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_github_api.delete_branch.return_value = True

        result = await github_delete_branch.fn(
            owner="test-owner", repo="test-repo", branch="feature"
        )

        assert result is True
        mock_github_api.delete_branch.assert_called_once_with(
            "test-owner", "test-repo", "feature"
        )


@pytest.mark.asyncio
async def test_github_get_default_branch(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_github_api.get_default_branch.return_value = "main"

        result = await github_get_default_branch.fn(
            owner="test-owner", repo="test-repo"
        )

        assert result == "main"
        mock_github_api.get_default_branch.assert_called_once_with(
            "test-owner", "test-repo"
        )


@pytest.mark.asyncio
async def test_github_set_default_branch(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_github_api.set_default_branch.return_value = True

        result = await github_set_default_branch.fn(
            owner="test-owner", repo="test-repo", branch="main"
        )

        assert result is True
        mock_github_api.set_default_branch.assert_called_once_with(
            "test-owner", "test-repo", "main"
        )


@pytest.mark.asyncio
async def test_github_list_pull_requests(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_pr1 = MagicMock()
        mock_pr1.title = "PR 1"
        mock_pr2 = MagicMock()
        mock_pr2.title = "PR 2"
        mock_github_api.list_pull_requests.return_value = [mock_pr1, mock_pr2]

        result = await github_list_pull_requests.fn(
            owner="test-owner", repo="test-repo", state="open", page=1, per_page=30
        )

        assert len(result) == 2
        assert result[0].title == "PR 1"
        assert result[1].title == "PR 2"
        mock_github_api.list_pull_requests.assert_called_once_with(
            "test-owner", "test-repo", "open", None, None, 1, 30
        )


@pytest.mark.asyncio
async def test_github_merge_pull_request(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        # Mock the merge_pull_request method to return True
        mock_github_api.merge_pull_request = MagicMock()
        mock_github_api.merge_pull_request.return_value = True

        result = await github_merge_pull_request.fn(
            owner="test-owner",
            repo="test-repo",
            pull_number=1,
            commit_title="Merge PR",
            commit_message="Merging PR #1",
            merge_method="merge",
        )

        assert result is True
        mock_github_api.merge_pull_request.assert_called_once_with(
            "test-owner", "test-repo", 1, "Merge PR", "Merging PR #1", "merge"
        )


@pytest.mark.asyncio
async def test_github_add_pull_request_review(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_review = MagicMock()
        mock_review.state = "APPROVED"
        mock_github_api.add_pull_request_review.return_value = mock_review

        result = await github_add_pull_request_review.fn(
            owner="test-owner",
            repo="test-repo",
            pull_number=1,
            event="APPROVE",
            body="LGTM",
        )

        assert result.state == "APPROVED"
        mock_github_api.add_pull_request_review.assert_called_once_with(
            "test-owner", "test-repo", 1, "APPROVE", "LGTM"
        )


@pytest.mark.asyncio
async def test_github_add_pull_request_comment(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_comment = MagicMock()
        mock_comment.body = "Test comment"
        mock_github_api.add_pull_request_comment.return_value = mock_comment

        result = await github_add_pull_request_comment.fn(
            owner="test-owner",
            repo="test-repo",
            pull_number=1,
            body="Test comment",
            commit_id="abc123",
            path="file.py",
            line=10,
            side="RIGHT",
        )

        assert result.body == "Test comment"
        mock_github_api.add_pull_request_comment.assert_called_once_with(
            "test-owner",
            "test-repo",
            1,
            "Test comment",
            "abc123",
            "file.py",
            10,
            "RIGHT",
        )


@pytest.mark.asyncio
async def test_github_list_pull_request_files(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_file1 = MagicMock()
        mock_file1.filename = "file1.py"
        mock_file2 = MagicMock()
        mock_file2.filename = "file2.py"
        mock_github_api.list_pull_request_files.return_value = [mock_file1, mock_file2]

        result = await github_list_pull_request_files.fn(
            owner="test-owner", repo="test-repo", pull_number=1
        )

        assert len(result) == 2
        assert result[0].filename == "file1.py"
        assert result[1].filename == "file2.py"
        mock_github_api.list_pull_request_files.assert_called_once_with(
            "test-owner", "test-repo", 1
        )


@pytest.mark.asyncio
async def test_github_update_pull_request(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_pr = MagicMock()
        mock_pr.title = "Updated PR"
        mock_github_api.update_pull_request.return_value = mock_pr

        result = await github_update_pull_request.fn(
            owner="test-owner",
            repo="test-repo",
            pull_number=1,
            title="Updated PR",
            body="Updated description",
            state="closed",
            base="main",
        )

        assert result.title == "Updated PR"
        mock_github_api.update_pull_request.assert_called_once_with(
            "test-owner",
            "test-repo",
            1,
            "Updated PR",
            "Updated description",
            "closed",
            "main",
        )


@pytest.mark.asyncio
async def test_github_list_issue_comments(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_comment1 = MagicMock()
        mock_comment1.body = "Comment 1"
        mock_comment2 = MagicMock()
        mock_comment2.body = "Comment 2"
        mock_github_api.list_issue_comments.return_value = [
            mock_comment1,
            mock_comment2,
        ]

        result = await github_list_issue_comments.fn(
            owner="test-owner", repo="test-repo", issue_number=1, page=1, per_page=30
        )

        assert len(result) == 2
        assert result[0].body == "Comment 1"
        assert result[1].body == "Comment 2"
        mock_github_api.list_issue_comments.assert_called_once_with(
            "test-owner", "test-repo", 1, 1, 30
        )


@pytest.mark.asyncio
async def test_github_add_labels(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_github_api.add_labels.return_value = True

        result = await github_add_labels.fn(
            owner="test-owner",
            repo="test-repo",
            issue_number=1,
            labels=["bug", "high-priority"],
        )

        assert result is True
        mock_github_api.add_labels.assert_called_once_with(
            "test-owner", "test-repo", 1, ["bug", "high-priority"]
        )


@pytest.mark.asyncio
async def test_github_remove_labels(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_github_api.remove_labels.return_value = True

        result = await github_remove_labels.fn(
            owner="test-owner",
            repo="test-repo",
            issue_number=1,
            labels=["bug", "high-priority"],
        )

        assert result is True
        mock_github_api.remove_labels.assert_called_once_with(
            "test-owner", "test-repo", 1, ["bug", "high-priority"]
        )


@pytest.mark.asyncio
async def test_github_list_labels(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_label1 = MagicMock()
        mock_label1.name = "bug"
        mock_label1.color = "ff0000"
        mock_label2 = MagicMock()
        mock_label2.name = "enhancement"
        mock_label2.color = "00ff00"
        mock_github_api.list_labels.return_value = [mock_label1, mock_label2]

        result = await github_list_labels.fn(
            owner="test-owner", repo="test-repo", page=1, per_page=30
        )

        assert len(result) == 2
        assert result[0].name == "bug"
        assert result[0].color == "ff0000"
        assert result[1].name == "enhancement"
        assert result[1].color == "00ff00"
        mock_github_api.list_labels.assert_called_once_with(
            "test-owner", "test-repo", 1, 30
        )


@pytest.mark.asyncio
async def test_github_create_label(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_label = MagicMock()
        mock_label.name = "bug"
        mock_label.color = "ff0000"
        mock_label.description = "Bug report"
        mock_github_api.create_label.return_value = mock_label

        result = await github_create_label.fn(
            owner="test-owner",
            repo="test-repo",
            name="bug",
            color="ff0000",
            description="Bug report",
        )

        assert result.name == "bug"
        assert result.color == "ff0000"
        assert result.description == "Bug report"
        mock_github_api.create_label.assert_called_once_with(
            "test-owner", "test-repo", "bug", "ff0000", "Bug report"
        )


@pytest.mark.asyncio
async def test_github_list_directory_contents(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_file = MagicMock()
        mock_file.path = "file.py"
        mock_file.type = "file"
        mock_dir = MagicMock()
        mock_dir.path = "src"
        mock_dir.type = "dir"
        mock_github_api.list_directory_contents.return_value = [mock_file, mock_dir]

        result = await github_list_directory_contents.fn(
            owner="test-owner", repo="test-repo", path="/", branch="main"
        )

        assert len(result) == 2
        assert result[0].path == "file.py"
        assert result[0].type == "file"
        assert result[1].path == "src"
        assert result[1].type == "dir"
        mock_github_api.list_directory_contents.assert_called_once_with(
            "test-owner", "test-repo", "/", "main"
        )


@pytest.mark.asyncio
async def test_github_delete_file(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_github_api.delete_file.return_value = True

        result = await github_delete_file.fn(
            owner="test-owner",
            repo="test-repo",
            path="file.py",
            message="Delete file",
            branch="main",
        )

        assert result is True
        mock_github_api.delete_file.assert_called_once_with(
            "test-owner", "test-repo", "file.py", "Delete file", "main"
        )


@pytest.mark.asyncio
async def test_github_compare_commits(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_comparison = MagicMock()
        mock_comparison.ahead_by = 2
        mock_comparison.behind_by = 1
        mock_github_api.compare_commits.return_value = mock_comparison

        result = await github_compare_commits.fn(
            owner="test-owner", repo="test-repo", base="main", head="feature"
        )

        assert result.ahead_by == 2
        assert result.behind_by == 1
        mock_github_api.compare_commits.assert_called_once_with(
            "test-owner", "test-repo", "main", "feature"
        )


@pytest.mark.asyncio
async def test_github_get_commit(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_commit = MagicMock()
        mock_commit.sha = "abc123"
        mock_commit.commit.message = "Test commit"
        mock_github_api.get_commit.return_value = mock_commit

        result = await github_get_commit.fn(
            owner="test-owner", repo="test-repo", sha="abc123"
        )

        assert result.sha == "abc123"
        assert result.commit.message == "Test commit"
        mock_github_api.get_commit.assert_called_once_with(
            "test-owner", "test-repo", "abc123"
        )


@pytest.mark.asyncio
async def test_github_create_release(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_release = MagicMock()
        mock_release.tag_name = "v1.0.0"
        mock_release.title = "Version 1.0.0"
        mock_github_api.create_release.return_value = mock_release

        result = await github_create_release.fn(
            owner="test-owner",
            repo="test-repo",
            tag="v1.0.0",
            name="Version 1.0.0",
            body="Release notes",
            draft=False,
            prerelease=False,
            target_commitish="main",
        )

        assert result.tag_name == "v1.0.0"
        assert result.title == "Version 1.0.0"
        mock_github_api.create_release.assert_called_once_with(
            "test-owner",
            "test-repo",
            "v1.0.0",
            "Version 1.0.0",
            "Release notes",
            False,
            False,
            "main",
        )


@pytest.mark.asyncio
async def test_github_list_releases(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_release1 = MagicMock()
        mock_release1.tag_name = "v1.0.0"
        mock_release2 = MagicMock()
        mock_release2.tag_name = "v1.1.0"
        mock_github_api.list_releases.return_value = [mock_release1, mock_release2]

        result = await github_list_releases.fn(
            owner="test-owner", repo="test-repo", page=1, per_page=30
        )

        assert len(result) == 2
        assert result[0].tag_name == "v1.0.0"
        assert result[1].tag_name == "v1.1.0"
        mock_github_api.list_releases.assert_called_once_with(
            "test-owner", "test-repo", 1, 30
        )


@pytest.mark.asyncio
async def test_github_list_collaborators(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_user1 = MagicMock()
        mock_user1.login = "user1"
        mock_user2 = MagicMock()
        mock_user2.login = "user2"
        mock_github_api.list_collaborators.return_value = [mock_user1, mock_user2]

        result = await github_list_collaborators.fn(
            owner="test-owner", repo="test-repo", page=1, per_page=30
        )

        assert len(result) == 2
        assert result[0].login == "user1"
        assert result[1].login == "user2"
        mock_github_api.list_collaborators.assert_called_once_with(
            "test-owner", "test-repo", 1, 30
        )


@pytest.mark.asyncio
async def test_github_add_collaborator(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_github_api.add_collaborator.return_value = True

        result = await github_add_collaborator.fn(
            owner="test-owner", repo="test-repo", username="new-user", permission="push"
        )

        assert result is True
        mock_github_api.add_collaborator.assert_called_once_with(
            "test-owner", "test-repo", "new-user", "push"
        )


@pytest.mark.asyncio
async def test_github_remove_collaborator(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_github_api.remove_collaborator.return_value = True

        result = await github_remove_collaborator.fn(
            owner="test-owner", repo="test-repo", username="old-user"
        )

        assert result is True
        mock_github_api.remove_collaborator.assert_called_once_with(
            "test-owner", "test-repo", "old-user"
        )


@pytest.mark.asyncio
async def test_github_get_repository_permissions(mock_github_api):
    with patch(
        "pyramidpy_tools.github.tools.get_github_api", return_value=mock_github_api
    ):
        mock_permissions = MagicMock()
        mock_permissions.admin = True
        mock_permissions.push = True
        mock_permissions.pull = True
        mock_github_api.get_repository_permissions.return_value = mock_permissions

        result = await github_get_repository_permissions.fn(
            owner="test-owner", repo="test-repo", username="test-user"
        )

        assert result.admin is True
        assert result.push is True
        assert result.pull is True
        mock_github_api.get_repository_permissions.assert_called_once_with(
            "test-owner", "test-repo", "test-user"
        )
