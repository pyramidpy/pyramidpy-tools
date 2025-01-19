import asyncio
import base64
from typing import List, Optional

from github import Github, GithubObject, Auth
from github.ContentFile import ContentFile
from github.GithubException import GithubException
from github.Repository import Repository, InputGitAuthor

from .schemas import (
    CreateBranchOptions,
    CreateIssueOptions,
    CreatePullRequestOptions,
    CreateRepositoryOptions,
    FileOperation,
    GitHubAuth,
)


def to_github_optional(value):
    """Convert None to GithubObject.NotSet for PyGitHub API calls."""
    return GithubObject.NotSet if value is None else value


class GitHubAPI:
    def __init__(self, auth: GitHubAuth):
        self.auth = auth
        self.github = Github(auth=Auth.Token(auth.token))
        self.loop = asyncio.get_event_loop()

    async def _run_sync(self, func, *args, **kwargs):
        """Run a synchronous PyGitHub function in the thread pool."""
        return await self.loop.run_in_executor(None, lambda: func(*args, **kwargs))

    async def _get_repo(self, owner: str, repo: str) -> Repository:
        """Get a repository by owner and name."""
        return await self._run_sync(self.github.get_repo, f"{owner}/{repo}")

    async def fork_repository(
        self, owner: str, repo: str, organization: Optional[str] = None
    ):
        repository = await self._get_repo(owner, repo)
        return await self._run_sync(
            repository.create_fork, organization=to_github_optional(organization)
        )

    async def create_branch(self, owner: str, repo: str, options: CreateBranchOptions):
        repository = await self._get_repo(owner, repo)
        return await self._run_sync(
            repository.create_git_ref, f"refs/heads/{options.ref}", options.sha
        )

    async def get_default_branch_sha(self, owner: str, repo: str) -> str:
        repository = await self._get_repo(owner, repo)
        try:
            main_branch = await self._run_sync(repository.get_branch, "main")
            return main_branch.commit.sha
        except GithubException:
            master_branch = await self._run_sync(repository.get_branch, "master")
            return master_branch.commit.sha

    async def get_file_contents(
        self, owner: str, repo: str, path: str, branch: Optional[str] = None
    ):
        repository = await self._get_repo(owner, repo)
        contents = await self._run_sync(
            repository.get_contents, path, ref=to_github_optional(branch)
        )

        if isinstance(contents, ContentFile):
            return contents
        else:
            raise ValueError("Path does not point to a file")

    async def create_issue(self, owner: str, repo: str, options: CreateIssueOptions):
        repository = await self._get_repo(owner, repo)
        return await self._run_sync(
            repository.create_issue,
            title=options.title,
            body=to_github_optional(options.body),
            assignees=to_github_optional(options.assignees),
            milestone=to_github_optional(options.milestone),
            labels=to_github_optional(options.labels),
        )

    async def create_pull_request(
        self, owner: str, repo: str, options: CreatePullRequestOptions
    ):
        repository = await self._get_repo(owner, repo)
        return await self._run_sync(
            repository.create_pull,
            title=options.title,
            body=to_github_optional(options.body),
            head=options.head,
            base=options.base,
            draft=to_github_optional(options.draft),
            maintainer_can_modify=to_github_optional(options.maintainer_can_modify),
        )

    async def create_or_update_file(
        self,
        owner: str,
        repo: str,
        path: str,
        content: str,
        message: str,
        branch: str,
        sha: Optional[str] = None,
        committer: Optional[InputGitAuthor] = None,
        author: Optional[InputGitAuthor] = None,
    ):
        repository = await self._get_repo(owner, repo)
        encoded_content = base64.b64encode(content.encode()).decode()

        return await self._run_sync(
            repository.update_file if sha else repository.create_file,
            path=path,
            message=message,
            content=encoded_content,
            branch=branch,
        )

    async def push_files(
        self,
        owner: str,
        repo: str,
        branch: str,
        files: List[FileOperation],
        message: str,
    ):
        repository = await self._get_repo(owner, repo)

        # Get the current commit SHA
        ref = await self._run_sync(repository.get_git_ref, f"heads/{branch}")
        base_tree = await self._run_sync(repository.get_git_tree, ref.object.sha)

        # Create tree
        tree_elements = []
        for file in files:
            if file.operation == "create" or file.operation == "update":
                blob = await self._run_sync(
                    repository.create_git_blob, content=file.content, encoding="utf-8"
                )
                tree_elements.append(
                    {
                        "path": file.path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob.sha,
                    }
                )

        new_tree = await self._run_sync(
            repository.create_git_tree, tree_elements, base_tree
        )

        # Create commit
        commit = await self._run_sync(
            repository.create_git_commit,
            message=message,
            tree=new_tree,
            parents=[ref.object],
        )

        # Update reference
        return await self._run_sync(ref.edit, sha=commit.sha, force=True)

    async def search_repositories(self, query: str, page: int = 1, per_page: int = 30):
        repositories = await self._run_sync(
            self.github.search_repositories, query=query
        )

        # Manual pagination since PyGitHub handles it differently
        start = (page - 1) * per_page
        end = start + per_page

        return list(repositories)[start:end]

    async def create_repository(self, options: CreateRepositoryOptions):
        return await self._run_sync(
            self.github.get_user().create_repo,
            name=options.name,
            description=to_github_optional(options.description),
            private=options.private,
            has_issues=to_github_optional(False),
            has_wiki=to_github_optional(False),
            has_downloads=to_github_optional(False),
            auto_init=to_github_optional(options.auto_init),
        )

    async def list_commits(
        self,
        owner: str,
        repo: str,
        page: int = 1,
        per_page: int = 30,
        sha: Optional[str] = None,
    ):
        repository = await self._get_repo(owner, repo)
        commits = await self._run_sync(
            repository.get_commits, sha=to_github_optional(sha)
        )

        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page

        return list(commits)[start:end]

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
    ):
        repository = await self._get_repo(owner, repo)
        issues = await self._run_sync(
            repository.get_issues,
            state=to_github_optional(state),
            labels=to_github_optional(labels),
            sort=to_github_optional(sort),
            direction=to_github_optional(direction),
            since=to_github_optional(since),
        )

        # Handle pagination
        if page and per_page:
            start = (page - 1) * per_page
            end = start + per_page
            return list(issues)[start:end]

        return list(issues)

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
    ):
        repository = await self._get_repo(owner, repo)
        issue = await self._run_sync(repository.get_issue, issue_number)

        # Update the issue
        return await self._run_sync(
            issue.edit,
            title=to_github_optional(title),
            body=to_github_optional(body),
            state=to_github_optional(state),
            labels=to_github_optional(labels),
            assignees=to_github_optional(assignees),
            milestone=to_github_optional(milestone),
        )

    async def add_issue_comment(
        self, owner: str, repo: str, issue_number: int, body: str
    ):
        repository = await self._get_repo(owner, repo)
        issue = await self._run_sync(repository.get_issue, issue_number)

        return await self._run_sync(issue.create_comment, body)

    async def list_branches(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30
    ):
        """List branches in a repository with pagination."""
        repository = await self._get_repo(owner, repo)
        branches = await self._run_sync(repository.get_branches)
        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page
        return list(branches)[start:end]

    async def delete_branch(self, owner: str, repo: str, branch: str) -> bool:
        """Delete a branch from a repository."""
        repository = await self._get_repo(owner, repo)
        ref = await self._run_sync(repository.get_git_ref, f"heads/{branch}")
        await self._run_sync(ref.delete)
        return True

    async def get_default_branch(self, owner: str, repo: str) -> str:
        """Get the default branch of a repository."""
        repository = await self._get_repo(owner, repo)
        return await self._run_sync(lambda: repository.default_branch)

    async def set_default_branch(self, owner: str, repo: str, branch: str) -> bool:
        """Set the default branch of a repository."""
        repository = await self._get_repo(owner, repo)
        await self._run_sync(repository.edit, default_branch=branch)
        return True

    async def list_pull_requests(
        self,
        owner: str,
        repo: str,
        state: Optional[str] = "open",
        sort: Optional[str] = None,
        direction: Optional[str] = None,
        page: int = 1,
        per_page: int = 30,
    ):
        """List pull requests in a repository with filters and pagination."""
        repository = await self._get_repo(owner, repo)
        pulls = await self._run_sync(
            repository.get_pulls,
            state=to_github_optional(state),
            sort=to_github_optional(sort),
            direction=to_github_optional(direction),
        )
        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page
        return list(pulls)[start:end]

    async def merge_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        commit_title: Optional[str] = None,
        commit_message: Optional[str] = None,
        merge_method: str = "merge",
    ):
        """Merge a pull request with specified strategy."""
        repository = await self._get_repo(owner, repo)
        pull = await self._run_sync(repository.get_pull, pull_number)
        return await self._run_sync(
            pull.merge,
            commit_title=to_github_optional(commit_title),
            commit_message=to_github_optional(commit_message),
            merge_method=merge_method,
        )

    async def add_pull_request_review(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        event: str,
        body: Optional[str] = None,
    ):
        """Add a review to a pull request."""
        repository = await self._get_repo(owner, repo)
        pull = await self._run_sync(repository.get_pull, pull_number)
        return await self._run_sync(
            pull.create_review, event=event, body=to_github_optional(body)
        )

    async def add_pull_request_comment(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        body: str,
        commit_id: str,
        path: str,
        line: int,
        side: str = "RIGHT",
    ):
        """Add a review comment to specific lines in a pull request."""
        repository = await self._get_repo(owner, repo)
        pull = await self._run_sync(repository.get_pull, pull_number)
        return await self._run_sync(
            pull.create_review_comment,
            body=body,
            commit_id=commit_id,
            path=path,
            line=line,
            side=side,
        )

    async def list_pull_request_files(self, owner: str, repo: str, pull_number: int):
        """List files changed in a pull request."""
        repository = await self._get_repo(owner, repo)
        pull = await self._run_sync(repository.get_pull, pull_number)
        return list(await self._run_sync(pull.get_files))

    async def update_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        base: Optional[str] = None,
    ):
        """Update a pull request's details."""
        repository = await self._get_repo(owner, repo)
        pull = await self._run_sync(repository.get_pull, pull_number)
        return await self._run_sync(
            pull.edit,
            title=to_github_optional(title),
            body=to_github_optional(body),
            state=to_github_optional(state),
            base=to_github_optional(base),
        )

    async def list_issue_comments(
        self,
        owner: str,
        repo: str,
        issue_number: int,
        page: int = 1,
        per_page: int = 30,
    ):
        """List comments on an issue with pagination."""
        repository = await self._get_repo(owner, repo)
        issue = await self._run_sync(repository.get_issue, issue_number)
        comments = await self._run_sync(issue.get_comments)
        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page
        return list(comments)[start:end]

    async def add_labels(
        self, owner: str, repo: str, issue_number: int, labels: List[str]
    ):
        """Add labels to an issue or pull request."""
        repository = await self._get_repo(owner, repo)
        issue = await self._run_sync(repository.get_issue, issue_number)
        await self._run_sync(issue.add_to_labels, *labels)
        return True

    async def remove_labels(
        self, owner: str, repo: str, issue_number: int, labels: List[str]
    ):
        """Remove labels from an issue or pull request."""
        repository = await self._get_repo(owner, repo)
        issue = await self._run_sync(repository.get_issue, issue_number)
        for label in labels:
            await self._run_sync(issue.remove_from_labels, label)
        return True

    async def list_labels(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30
    ):
        """List all labels in a repository with pagination."""
        repository = await self._get_repo(owner, repo)
        labels = await self._run_sync(repository.get_labels)
        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page
        return list(labels)[start:end]

    async def create_label(
        self,
        owner: str,
        repo: str,
        name: str,
        color: str,
        description: Optional[str] = None,
    ):
        """Create a new label in a repository."""
        repository = await self._get_repo(owner, repo)
        return await self._run_sync(
            repository.create_label,
            name=name,
            color=color,
            description=to_github_optional(description),
        )

    async def list_directory_contents(
        self, owner: str, repo: str, path: str, branch: Optional[str] = None
    ):
        """List contents of a directory in a repository."""
        repository = await self._get_repo(owner, repo)
        contents = await self._run_sync(
            repository.get_contents, path, ref=to_github_optional(branch)
        )
        return contents if isinstance(contents, list) else [contents]

    async def delete_file(
        self,
        owner: str,
        repo: str,
        path: str,
        message: str,
        branch: Optional[str] = None,
    ) -> bool:
        """Delete a file from a repository."""
        repository = await self._get_repo(owner, repo)
        contents = await self._run_sync(
            repository.get_contents, path, ref=to_github_optional(branch)
        )
        await self._run_sync(
            repository.delete_file,
            path=path,
            message=message,
            sha=contents.sha,
            branch=to_github_optional(branch),
        )
        return True

    async def compare_commits(self, owner: str, repo: str, base: str, head: str):
        """Compare changes between commits or branches."""
        repository = await self._get_repo(owner, repo)
        return await self._run_sync(repository.compare, base, head)

    async def get_commit(self, owner: str, repo: str, sha: str):
        """Get detailed information about a specific commit."""
        repository = await self._get_repo(owner, repo)
        return await self._run_sync(repository.get_commit, sha)

    async def create_release(
        self,
        owner: str,
        repo: str,
        tag: str,
        name: str,
        body: Optional[str] = None,
        draft: bool = False,
        prerelease: bool = False,
        target_commitish: Optional[str] = None,
    ):
        """Create a new release in a repository."""
        repository = await self._get_repo(owner, repo)
        return await self._run_sync(
            repository.create_git_release,
            tag=tag,
            name=name,
            message=to_github_optional(body),
            draft=draft,
            prerelease=prerelease,
            target_commitish=to_github_optional(target_commitish),
        )

    async def list_releases(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30
    ):
        """List releases in a repository with pagination."""
        repository = await self._get_repo(owner, repo)
        releases = await self._run_sync(repository.get_releases)
        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page
        return list(releases)[start:end]

    async def list_collaborators(
        self, owner: str, repo: str, page: int = 1, per_page: int = 30
    ):
        """List collaborators of a repository with pagination."""
        repository = await self._get_repo(owner, repo)
        collaborators = await self._run_sync(repository.get_collaborators)
        # Manual pagination
        start = (page - 1) * per_page
        end = start + per_page
        return list(collaborators)[start:end]

    async def add_collaborator(
        self, owner: str, repo: str, username: str, permission: Optional[str] = None
    ) -> bool:
        """Add a collaborator to a repository."""
        repository = await self._get_repo(owner, repo)
        await self._run_sync(
            repository.add_to_collaborators,
            username,
            permission=to_github_optional(permission),
        )
        return True

    async def remove_collaborator(self, owner: str, repo: str, username: str) -> bool:
        """Remove a collaborator from a repository."""
        repository = await self._get_repo(owner, repo)
        await self._run_sync(repository.remove_from_collaborators, username)
        return True

    async def get_repository_permissions(self, owner: str, repo: str, username: str):
        """Check permissions for a user in a repository."""
        repository = await self._get_repo(owner, repo)
        return await self._run_sync(repository.get_collaborator_permission, username)
