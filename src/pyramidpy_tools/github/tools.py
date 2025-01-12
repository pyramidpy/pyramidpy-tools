from datetime import datetime
from typing import List, Optional

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool

from pyramidpy_tools.toolkit import Toolkit

from .base import GitHubAPI
from .schemas import (
    CreateBranchOptions,
    CreateIssueOptions,
    CreatePullRequestOptions,
    CreateRepositoryOptions,
    FileOperation,
)


def get_github_api() -> GitHubAPI:
    """Get GitHub API instance with token from context if available"""
    flow = get_flow()
    if flow and flow.context:
        token = flow.context.get("github_token")
        if token:
            return GitHubAPI(token=token)
    return GitHubAPI()


@tool(
    name="github_fork_repository",
    description="Fork a GitHub repository to your account or specified organization",
    include_return_description=False,
)
async def github_fork_repository(
    owner: str, repo: str, organization: Optional[str] = None
):
    github = get_github_api()
    return await github.fork_repository(owner, repo, organization)


@tool(
    name="github_create_branch",
    description="Create a new branch in a GitHub repository",
    include_return_description=False,
)
async def github_create_branch(
    owner: str, repo: str, branch: str, from_branch: Optional[str] = None
):
    github = get_github_api()
    if from_branch:
        try:
            response = await github._make_request(
                "GET", f"repos/{owner}/{repo}/git/refs/heads/{from_branch}"
            )
            sha = response["object"]["sha"]
        except Exception:
            raise ValueError(f"Source branch '{from_branch}' not found")
    else:
        sha = await github.get_default_branch_sha(owner, repo)

    options = CreateBranchOptions(ref=branch, sha=sha)
    return await github.create_branch(owner, repo, options)


@tool(
    name="github_get_file_contents",
    description="Get the contents of a file or directory from a GitHub repository",
    include_return_description=False,
)
async def github_get_file_contents(
    owner: str, repo: str, path: str, branch: Optional[str] = None
):
    github = get_github_api()
    return await github.get_file_contents(owner, repo, path, branch)


@tool(
    name="github_create_issue",
    description="Create a new issue in a GitHub repository",
    include_return_description=False,
)
async def github_create_issue(
    owner: str,
    repo: str,
    title: str,
    body: Optional[str] = None,
    assignees: Optional[List[str]] = None,
    labels: Optional[List[str]] = None,
    milestone: Optional[int] = None,
):
    github = get_github_api()
    options = CreateIssueOptions(
        title=title, body=body, assignees=assignees, labels=labels, milestone=milestone
    )
    return await github.create_issue(owner, repo, options)


@tool(
    name="github_create_pull_request",
    description="Create a new pull request in a GitHub repository",
    include_return_description=False,
)
async def github_create_pull_request(
    owner: str,
    repo: str,
    title: str,
    head: str,
    base: str,
    body: Optional[str] = None,
    draft: Optional[bool] = None,
    maintainer_can_modify: Optional[bool] = None,
):
    github = get_github_api()
    options = CreatePullRequestOptions(
        title=title,
        head=head,
        base=base,
        body=body,
        draft=draft,
        maintainer_can_modify=maintainer_can_modify,
    )
    return await github.create_pull_request(owner, repo, options)


@tool(
    name="github_create_or_update_file",
    description="Create or update a single file in a GitHub repository",
    include_return_description=False,
)
async def github_create_or_update_file(
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: str,
    sha: Optional[str] = None,
):
    github = get_github_api()
    return await github.create_or_update_file(
        owner, repo, path, content, message, branch, sha
    )


@tool(
    name="github_push_files",
    description="Push multiple files to a GitHub repository in a single commit",
    include_return_description=False,
)
async def github_push_files(
    owner: str, repo: str, branch: str, files: List[FileOperation], message: str
):
    github = get_github_api()
    return await github.push_files(owner, repo, branch, files, message)


@tool(
    name="github_search_repositories",
    description="Search for GitHub repositories",
    include_return_description=False,
)
async def github_search_repositories(query: str, page: int = 1, per_page: int = 30):
    github = get_github_api()
    return await github.search_repositories(query, page, per_page)


@tool(
    name="github_create_repository",
    description="Create a new GitHub repository in your account",
    include_return_description=False,
)
async def github_create_repository(
    name: str,
    description: Optional[str] = None,
    private: Optional[bool] = None,
    auto_init: Optional[bool] = None,
):
    github = get_github_api()
    options = CreateRepositoryOptions(
        name=name, description=description, private=private, auto_init=auto_init
    )
    return await github.create_repository(options)


@tool(
    name="github_list_commits",
    description="Get list of commits of a branch in a GitHub repository",
    include_return_description=False,
)
async def github_list_commits(
    owner: str, repo: str, page: int = 1, per_page: int = 30, sha: Optional[str] = None
):
    github = get_github_api()
    return await github.list_commits(owner, repo, page, per_page, sha)


@tool(
    name="github_list_issues",
    description="List issues in a GitHub repository with filtering options",
    include_return_description=False,
)
async def github_list_issues(
    owner: str,
    repo: str,
    state: Optional[str] = None,
    labels: Optional[List[str]] = None,
    sort: Optional[str] = None,
    direction: Optional[str] = None,
    since: Optional[str] = None,
    page: Optional[int] = None,
    per_page: Optional[int] = None,
):
    github = get_github_api()
    return await github.list_issues(
        owner, repo, state, labels, sort, direction, since, page, per_page
    )


@tool(
    name="github_update_issue",
    description="Update an existing issue in a GitHub repository",
    include_return_description=False,
)
async def github_update_issue(
    owner: str,
    repo: str,
    issue_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    state: Optional[str] = None,
    labels: Optional[List[str]] = None,
    assignees: Optional[List[str]] = None,
    milestone: Optional[int] = None,
):
    github = get_github_api()
    return await github.update_issue(
        owner, repo, issue_number, title, body, state, labels, assignees, milestone
    )


@tool(
    name="github_add_issue_comment",
    description="Add a comment to an existing issue",
    include_return_description=False,
)
async def github_add_issue_comment(owner: str, repo: str, issue_number: int, body: str):
    github = get_github_api()
    return await github.add_issue_comment(owner, repo, issue_number, body)


@tool(
    name="github_get_issue",
    description="Get details of a specific issue in a GitHub repository",
    include_return_description=False,
)
async def github_get_issue(owner: str, repo: str, issue_number: int):
    github = get_github_api()
    return await github.get_issue(owner, repo, issue_number)


github_toolkit = Toolkit.create_toolkit(
    id="github_toolkit",
    tools=[
        github_fork_repository,
        github_create_branch,
        github_get_file_contents,
        github_create_issue,
        github_create_pull_request,
        github_create_or_update_file,
        github_push_files,
        github_search_repositories,
        github_create_repository,
        github_list_commits,
        github_list_issues,
        github_update_issue,
        github_add_issue_comment,
        github_get_issue,
    ],
    auth_key="github_token",
    requires_config=True,
    is_app_default=True,
    name="GitHub Toolkit",
    description="Tools for interacting with GitHub API",
)
