from typing import Any, List, Optional
from github import GithubObject

from controlflow.flows.flow import get_flow
from controlflow.tools.tools import tool
from pyramidpy_tools.settings import settings
from pyramidpy_tools.toolkit import Toolkit

from .base import GitHubAPI
from .schemas import (
    CreateBranchOptions,
    CreateIssueOptions,
    CreatePullRequestOptions,
    CreateRepositoryOptions,
    FileOperation,
    GitHubAuth,
)

AUTH_KEY = "github_token"

def to_github_optional(value: Any) -> Any:
    """Convert None to GithubObject.NotSet for optional parameters."""
    return GithubObject.NotSet if value is None else value


def get_github_api() -> GitHubAPI:
    """Get GitHub API instance with token from context if available"""
    flow = get_flow()
    if flow and flow.context:
        auth = flow.context.get("auth", {}).get(AUTH_KEY)
        if auth:
            try:
                auth = GitHubAuth.model_validate(auth)
                return GitHubAPI(auth=auth)
            except Exception as e:
                raise ValueError(f"Invalid GitHub token: {e}")
    return GitHubAPI(auth=GitHubAuth(token=settings.tool_provider.github_token))


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
        # Get SHA from source branch using get_branch
        source_branch = await github.get_branch(owner, repo, from_branch)
        sha = source_branch.commit.sha
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
    print(owner, repo, state, labels, sort, direction, since, page, per_page)
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


@tool(
    name="github_list_branches",
    description="List all branches in a GitHub repository",
    include_return_description=False,
)
async def github_list_branches(
    owner: str,
    repo: str,
    page: int = 1,
    per_page: int = 30,
):
    github = get_github_api()
    return await github.list_branches(owner, repo, page, per_page)


@tool(
    name="github_delete_branch",
    description="Delete a branch from a GitHub repository",
    include_return_description=False,
)
async def github_delete_branch(
    owner: str,
    repo: str,
    branch: str,
):
    github = get_github_api()
    return await github.delete_branch(owner, repo, branch)


@tool(
    name="github_get_default_branch",
    description="Get the default branch of a GitHub repository",
    include_return_description=False,
)
async def github_get_default_branch(
    owner: str,
    repo: str,
):
    github = get_github_api()
    return await github.get_default_branch(owner, repo)


@tool(
    name="github_set_default_branch",
    description="Change the default branch of a GitHub repository",
    include_return_description=False,
)
async def github_set_default_branch(
    owner: str,
    repo: str,
    branch: str,
):
    github = get_github_api()
    return await github.set_default_branch(owner, repo, branch)


@tool(
    name="github_list_pull_requests",
    description="List pull requests in a GitHub repository with filters",
    include_return_description=False,
)
async def github_list_pull_requests(
    owner: str,
    repo: str,
    state: Optional[str] = "open",  # open, closed, or all
    sort: Optional[str] = None,  # created, updated, popularity, long-running
    direction: Optional[str] = None,  # asc or desc
    page: int = 1,
    per_page: int = 30,
):
    github = get_github_api()
    return await github.list_pull_requests(
        owner, repo, state, sort, direction, page, per_page
    )


@tool(
    name="github_get_pull_request",
    description="Get detailed information about a specific pull request",
    include_return_description=False,
)
async def github_get_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
):
    github = get_github_api()
    repository = await github._get_repo(owner, repo)
    return await github._run_sync(repository.get_pull, pull_number)


@tool(
    name="github_merge_pull_request",
    description="Merge a pull request with specified strategy",
    include_return_description=False,
)
async def github_merge_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
    commit_title: Optional[str] = None,
    commit_message: Optional[str] = None,
    merge_method: Optional[str] = "merge",  # merge, squash, or rebase
):
    github = get_github_api()
    return github.merge_pull_request(
        owner, repo, pull_number, commit_title, commit_message, merge_method
    )


@tool(
    name="github_add_pull_request_review",
    description="Add a review to a pull request",
    include_return_description=False,
)
async def github_add_pull_request_review(
    owner: str,
    repo: str,
    pull_number: int,
    event: str,  # APPROVE, REQUEST_CHANGES, or COMMENT
    body: Optional[str] = None,
):
    github = get_github_api()
    return await github.add_pull_request_review(owner, repo, pull_number, event, body)


@tool(
    name="github_add_pull_request_comment",
    description="Add a review comment to specific lines in a pull request",
    include_return_description=False,
)
async def github_add_pull_request_comment(
    owner: str,
    repo: str,
    pull_number: int,
    body: str,
    commit_id: str,
    path: str,
    line: int,
    side: str = "RIGHT",  # LEFT for deletions, RIGHT for additions
):
    github = get_github_api()
    return await github.add_pull_request_comment(
        owner, repo, pull_number, body, commit_id, path, line, side
    )


@tool(
    name="github_list_pull_request_files",
    description="List files changed in a pull request",
    include_return_description=False,
)
async def github_list_pull_request_files(
    owner: str,
    repo: str,
    pull_number: int,
):
    github = get_github_api()
    return await github.list_pull_request_files(owner, repo, pull_number)


@tool(
    name="github_update_pull_request",
    description="Update a pull request's details",
    include_return_description=False,
)
async def github_update_pull_request(
    owner: str,
    repo: str,
    pull_number: int,
    title: Optional[str] = None,
    body: Optional[str] = None,
    state: Optional[str] = None,  # open or closed
    base: Optional[str] = None,  # The name of the branch to merge into
):
    github = get_github_api()
    return await github.update_pull_request(
        owner, repo, pull_number, title, body, state, base
    )


@tool(
    name="github_list_issue_comments",
    description="Get all comments on a GitHub issue",
    include_return_description=False,
)
async def github_list_issue_comments(
    owner: str,
    repo: str,
    issue_number: int,
    page: int = 1,
    per_page: int = 30,
):
    github = get_github_api()
    return await github.list_issue_comments(owner, repo, issue_number, page, per_page)


@tool(
    name="github_add_labels",
    description="Add labels to a GitHub issue or pull request",
    include_return_description=False,
)
async def github_add_labels(
    owner: str,
    repo: str,
    issue_number: int,
    labels: List[str],
):
    github = get_github_api()
    return await github.add_labels(owner, repo, issue_number, labels)


@tool(
    name="github_remove_labels",
    description="Remove labels from a GitHub issue or pull request",
    include_return_description=False,
)
async def github_remove_labels(
    owner: str,
    repo: str,
    issue_number: int,
    labels: List[str],
):
    github = get_github_api()
    return await github.remove_labels(owner, repo, issue_number, labels)


@tool(
    name="github_list_labels",
    description="List all labels available in a GitHub repository",
    include_return_description=False,
)
async def github_list_labels(
    owner: str,
    repo: str,
    page: int = 1,
    per_page: int = 30,
):
    github = get_github_api()
    return await github.list_labels(owner, repo, page, per_page)


@tool(
    name="github_create_label",
    description="Create a new label in a GitHub repository",
    include_return_description=False,
)
async def github_create_label(
    owner: str,
    repo: str,
    name: str,
    color: str,  # hex color without #
    description: Optional[str] = None,
):
    github = get_github_api()
    return await github.create_label(owner, repo, name, color, description)


@tool(
    name="github_list_directory_contents",
    description="List contents of a directory in a GitHub repository",
    include_return_description=False,
)
async def github_list_directory_contents(
    owner: str,
    repo: str,
    path: str,
    branch: Optional[str] = None,
):
    github = get_github_api()
    return await github.list_directory_contents(owner, repo, path, branch)


@tool(
    name="github_delete_file",
    description="Delete a file from a GitHub repository",
    include_return_description=False,
)
async def github_delete_file(
    owner: str,
    repo: str,
    path: str,
    message: str,
    branch: Optional[str] = None,
):
    github = get_github_api()
    return await github.delete_file(owner, repo, path, message, branch)


@tool(
    name="github_compare_commits",
    description="Compare changes between commits or branches",
    include_return_description=False,
)
async def github_compare_commits(
    owner: str,
    repo: str,
    base: str,
    head: str,
):
    github = get_github_api()
    return await github.compare_commits(owner, repo, base, head)


@tool(
    name="github_get_commit",
    description="Get detailed information about a specific commit",
    include_return_description=False,
)
async def github_get_commit(
    owner: str,
    repo: str,
    sha: str,
):
    github = get_github_api()
    return await github.get_commit(owner, repo, sha)


@tool(
    name="github_create_release",
    description="Create a new release in a GitHub repository",
    include_return_description=False,
)
async def github_create_release(
    owner: str,
    repo: str,
    tag: str,
    name: str,
    body: Optional[str] = None,
    draft: bool = False,
    prerelease: bool = False,
    target_commitish: Optional[str] = None,
):
    github = get_github_api()
    return await github.create_release(
        owner, repo, tag, name, body, draft, prerelease, target_commitish
    )


@tool(
    name="github_list_releases",
    description="List releases in a GitHub repository",
    include_return_description=False,
)
async def github_list_releases(
    owner: str,
    repo: str,
    page: int = 1,
    per_page: int = 30,
):
    github = get_github_api()
    return await github.list_releases(owner, repo, page, per_page)


@tool(
    name="github_list_collaborators",
    description="List collaborators of a GitHub repository",
    include_return_description=False,
)
async def github_list_collaborators(
    owner: str,
    repo: str,
    page: int = 1,
    per_page: int = 30,
):
    github = get_github_api()
    return await github.list_collaborators(owner, repo, page, per_page)


@tool(
    name="github_add_collaborator",
    description="Add a collaborator to a GitHub repository",
    include_return_description=False,
)
async def github_add_collaborator(
    owner: str,
    repo: str,
    username: str,
    permission: Optional[str] = None,  # pull, push, admin, maintain, triage
):
    github = get_github_api()
    return await github.add_collaborator(owner, repo, username, permission)


@tool(
    name="github_remove_collaborator",
    description="Remove a collaborator from a GitHub repository",
    include_return_description=False,
)
async def github_remove_collaborator(
    owner: str,
    repo: str,
    username: str,
):
    github = get_github_api()
    return await github.remove_collaborator(owner, repo, username)


@tool(
    name="github_get_repository_permissions",
    description="Check permissions for a user in a GitHub repository",
    include_return_description=False,
)
async def github_get_repository_permissions(
    owner: str,
    repo: str,
    username: str,
):
    github = get_github_api()
    return await github.get_repository_permissions(owner, repo, username)


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
        github_list_branches,
        github_delete_branch,
        github_get_default_branch,
        github_set_default_branch,
        github_list_pull_requests,
        github_get_pull_request,
        github_merge_pull_request,
        github_add_pull_request_review,
        github_add_pull_request_comment,
        github_list_pull_request_files,
        github_update_pull_request,
        github_list_issue_comments,
        github_add_labels,
        github_remove_labels,
        github_list_labels,
        github_create_label,
        github_list_directory_contents,
        github_delete_file,
        github_compare_commits,
        github_get_commit,
        github_create_release,
        github_list_releases,
        github_list_collaborators,
        github_add_collaborator,
        github_remove_collaborator,
        github_get_repository_permissions,
    ],
    auth_key=AUTH_KEY,
    requires_config=True,
    auth_config_schema=GitHubAuth,
    is_app_default=True,
    name="GitHub Toolkit",
    description="Tools for interacting with GitHub API",
)
