import base64
from datetime import datetime
from typing import List, Optional, Union

import httpx

from pyramidpy_tools.settings import settings

from .schemas import (
    CreateBranchOptions,
    CreateIssueOptions,
    CreatePullRequestOptions,
    CreateRepositoryOptions,
    FileOperation,
    GitHubCommit,
    GitHubContent,
    GitHubFork,
    GitHubIssue,
    GitHubPullRequest,
    GitHubReference,
    GitHubRepository,
    GitHubTree,
)


class GitHubAPI:
    def __init__(self, token: str = settings.tool_provider.github_token):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "github-mcp-server",
        }

    async def _make_request(
        self, method: str, endpoint: str, **kwargs
    ) -> Union[dict, List[dict]]:
        url = f"{self.base_url}/{endpoint}"
        async with httpx.AsyncClient() as client:
            response = await client.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def fork_repository(
        self, owner: str, repo: str, organization: Optional[str] = None
    ) -> GitHubFork:
        endpoint = f"repos/{owner}/{repo}/forks"
        params = {"organization": organization} if organization else None
        data = await self._make_request("POST", endpoint, params=params)
        return GitHubFork(**data)

    async def create_branch(
        self, owner: str, repo: str, options: CreateBranchOptions
    ) -> GitHubReference:
        endpoint = f"repos/{owner}/{repo}/git/refs"
        data = {"ref": f"refs/heads/{options.ref}", "sha": options.sha}
        response = await self._make_request("POST", endpoint, json=data)
        return GitHubReference(**response)

    async def get_default_branch_sha(self, owner: str, repo: str) -> str:
        try:
            response = await self._make_request(
                "GET", f"repos/{owner}/{repo}/git/refs/heads/main"
            )
        except httpx.HTTPError:
            response = await self._make_request(
                "GET", f"repos/{owner}/{repo}/git/refs/heads/master"
            )
        return response["object"]["sha"]

    async def get_file_contents(
        self, owner: str, repo: str, path: str, branch: Optional[str] = None
    ) -> GitHubContent:
        endpoint = f"repos/{owner}/{repo}/contents/{path}"
        params = {"ref": branch} if branch else None
        data = await self._make_request("GET", endpoint, params=params)

        if isinstance(data, dict) and data.get("content"):
            data["content"] = base64.b64decode(data["content"]).decode("utf-8")

        return GitHubContent(**data)

    async def create_issue(
        self, owner: str, repo: str, options: CreateIssueOptions
    ) -> GitHubIssue:
        endpoint = f"repos/{owner}/{repo}/issues"
        data = await self._make_request(
            "POST", endpoint, json=options.dict(exclude_none=True)
        )
        return GitHubIssue(**data)

    async def create_pull_request(
        self, owner: str, repo: str, options: CreatePullRequestOptions
    ) -> GitHubPullRequest:
        endpoint = f"repos/{owner}/{repo}/pulls"
        data = await self._make_request(
            "POST", endpoint, json=options.dict(exclude_none=True)
        )
        return GitHubPullRequest(**data)

    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
        sha: Optional[str] = None,
    ) -> dict:
        endpoint = f"repos/{owner}/{repo}/contents/{path}"
        data = {
            "message": message,
            "content": base64.b64encode(content.encode()).decode(),
            "branch": branch,
        }
        if sha:
            data["sha"] = sha

        response = await self._make_request("PUT", endpoint, json=data)
        return response

    async def create_tree(
        self,
        owner: str,
        repo: str,
        files: List[FileOperation],
        base_tree: Optional[str] = None,
    ) -> GitHubTree:
        endpoint = f"repos/{owner}/{repo}/git/trees"
        tree = [
            {
                "path": file.path,
                "mode": "100644",
                "type": "blob",
                "content": file.content,
            }
            for file in files
        ]

        data = {"tree": tree}
        if base_tree:
            data["base_tree"] = base_tree

        response = await self._make_request("POST", endpoint, json=data)
        return GitHubTree(**response)

    async def create_commit(
        self, owner: str, repo: str, message: str, tree: str, parents: List[str]
    ) -> GitHubCommit:
        endpoint = f"repos/{owner}/{repo}/git/commits"
        data = {"message": message, "tree": tree, "parents": parents}
        response = await self._make_request("POST", endpoint, json=data)
        return GitHubCommit(**response)

    async def update_reference(
        self, owner: str, repo: str, ref: str, sha: str
    ) -> GitHubReference:
        endpoint = f"repos/{owner}/{repo}/git/refs/{ref}"
        data = {"sha": sha, "force": True}
        response = await self._make_request("PATCH", endpoint, json=data)
        return GitHubReference(**response)

    async def push_files(
        self,
        owner: str,
        repo: str,
        branch: str,
        files: List[FileOperation],
        message: str,
    ) -> GitHubReference:
        # Get the current commit SHA
        ref_data = await self._make_request(
            "GET", f"repos/{owner}/{repo}/git/refs/heads/{branch}"
        )
        commit_sha = ref_data["object"]["sha"]

        # Create tree
        tree = await self.create_tree(owner, repo, files, commit_sha)

        # Create commit
        commit = await self.create_commit(owner, repo, message, tree.sha, [commit_sha])

        # Update reference
        return await self.update_reference(owner, repo, f"heads/{branch}", commit.sha)

    async def search_repositories(
        self, query: str, page: int = 1, per_page: int = 30
    ) -> List[GitHubRepository]:
        endpoint = "search/repositories"
        params = {"q": query, "page": page, "per_page": per_page}
        response = await self._make_request("GET", endpoint, params=params)
        return [GitHubRepository(**repo) for repo in response["items"]]

    async def create_repository(
        self, options: CreateRepositoryOptions
    ) -> GitHubRepository:
        endpoint = "user/repos"
        data = await self._make_request(
            "POST", endpoint, json=options.dict(exclude_none=True)
        )
        return GitHubRepository(**data)

    async def list_commits(
        self,
        owner: str,
        repo: str,
        page: int = 1,
        per_page: int = 30,
        sha: Optional[str] = None,
    ) -> List[GitHubCommit]:
        endpoint = f"repos/{owner}/{repo}/commits"
        params = {"page": page, "per_page": per_page}
        if sha:
            params["sha"] = sha

        data = await self._make_request("GET", endpoint, params=params)
        return [GitHubCommit(**commit) for commit in data]

    async def list_issues(
        self,
        owner: str,
        repo: str,
        state: Optional[str] = None,
        labels: Optional[List[str]] = None,
        sort: Optional[str] = None,
        direction: Optional[str] = None,
        since: Optional[str] = None,
        page: Optional[int] = None,
        per_page: Optional[int] = None,
    ) -> List[GitHubIssue]:
        endpoint = f"repos/{owner}/{repo}/issues"
        params = {}
        if state:
            params["state"] = state
        if labels:
            params["labels"] = ",".join(labels)
        if sort:
            params["sort"] = sort
        if direction:
            params["direction"] = direction
        if since:
            params["since"] = since
        if page:
            params["page"] = page
        if per_page:
            params["per_page"] = per_page

        data = await self._make_request("GET", endpoint, params=params)
        return [GitHubIssue(**issue) for issue in data]

    async def update_issue(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[int] = None,
    ) -> GitHubIssue:
        endpoint = f"repos/{owner}/{repo}/issues/{issue_number}"
        data = {}
        if title:
            data["title"] = title
        if body:
            data["body"] = body
        if state:
            data["state"] = state
        if labels:
            data["labels"] = labels
        if assignees:
            data["assignees"] = assignees
        if milestone:
            data["milestone"] = milestone

        response = await self._make_request("PATCH", endpoint, json=data)
        return GitHubIssue(**response)

    async def add_issue_comment(
        self, owner: str, repo: str, issue_number: int, body: str
    ) -> dict:
        endpoint = f"repos/{owner}/{repo}/issues/{issue_number}/comments"
        return await self._make_request("POST", endpoint, json={"body": body})

    async def get_issue(self, owner: str, repo: str, issue_number: int) -> GitHubIssue:
        endpoint = f"repos/{owner}/{repo}/issues/{issue_number}"
        data = await self._make_request("GET", endpoint)
        return GitHubIssue(**data)
