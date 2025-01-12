from datetime import datetime
from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field


class GitHubAuthor(BaseModel):
    name: str
    email: str
    date: str


class GitHubOwner(BaseModel):
    login: str
    id: int
    node_id: str
    avatar_url: str
    url: str
    html_url: str
    type: str


class GitHubRepository(BaseModel):
    id: int
    node_id: str
    name: str
    full_name: str
    private: bool
    owner: GitHubOwner
    html_url: str
    description: Optional[str] = None
    fork: bool
    url: str
    created_at: str
    updated_at: str
    pushed_at: str
    git_url: str
    ssh_url: str
    clone_url: str
    default_branch: str


class GitHubFileContent(BaseModel):
    type: str
    encoding: str
    size: int
    name: str
    path: str
    content: str
    sha: str
    url: str
    git_url: str
    html_url: str
    download_url: str


class GitHubDirectoryContent(BaseModel):
    type: str
    size: int
    name: str
    path: str
    sha: str
    url: str
    git_url: str
    html_url: str
    download_url: Optional[str] = None


GitHubContent = Union[GitHubFileContent, List[GitHubDirectoryContent]]


class FileOperation(BaseModel):
    path: str
    content: str


class GitHubTreeEntry(BaseModel):
    path: str
    mode: Literal["100644", "100755", "040000", "160000", "120000"]
    type: Literal["blob", "tree", "commit"]
    size: Optional[int] = None
    sha: str
    url: str


class GitHubTree(BaseModel):
    sha: str
    url: str
    tree: List[GitHubTreeEntry]
    truncated: bool


class GitHubCommit(BaseModel):
    sha: str
    node_id: str
    url: str
    author: GitHubAuthor
    committer: GitHubAuthor
    message: str
    tree: dict
    parents: List[dict]


class GitHubReference(BaseModel):
    ref: str
    node_id: str
    url: str
    object: dict


class GitHubLabel(BaseModel):
    id: int
    node_id: str
    url: str
    name: str
    color: str
    default: bool
    description: Optional[str] = None


class GitHubIssueAssignee(BaseModel):
    login: str
    id: int
    avatar_url: str
    url: str
    html_url: str


class GitHubMilestone(BaseModel):
    url: str
    html_url: str
    labels_url: str
    id: int
    node_id: str
    number: int
    title: str
    description: str
    state: str


class GitHubIssue(BaseModel):
    url: str
    repository_url: str
    labels_url: str
    comments_url: str
    events_url: str
    html_url: str
    id: int
    node_id: str
    number: int
    title: str
    user: GitHubIssueAssignee
    labels: List[GitHubLabel]
    state: str
    locked: bool
    assignee: Optional[GitHubIssueAssignee] = None
    assignees: List[GitHubIssueAssignee]
    milestone: Optional[GitHubMilestone] = None
    comments: int
    created_at: str
    updated_at: str
    closed_at: Optional[str] = None
    body: Optional[str] = None


class GitHubPullRequestHead(BaseModel):
    label: str
    ref: str
    sha: str
    user: GitHubIssueAssignee
    repo: GitHubRepository


class GitHubPullRequest(BaseModel):
    url: str
    id: int
    node_id: str
    html_url: str
    diff_url: str
    patch_url: str
    issue_url: str
    number: int
    state: str
    locked: bool
    title: str
    user: GitHubIssueAssignee
    body: str
    created_at: str
    updated_at: str
    closed_at: Optional[str] = None
    merged_at: Optional[str] = None
    merge_commit_sha: Optional[str] = None
    assignee: Optional[GitHubIssueAssignee] = None
    assignees: List[GitHubIssueAssignee]
    head: GitHubPullRequestHead
    base: GitHubPullRequestHead


# Input Models
class CreateRepositoryOptions(BaseModel):
    name: str
    description: Optional[str] = None
    private: Optional[bool] = None
    auto_init: Optional[bool] = None


class CreateIssueOptions(BaseModel):
    title: str
    body: Optional[str] = None
    assignees: Optional[List[str]] = None
    milestone: Optional[int] = None
    labels: Optional[List[str]] = None


class CreatePullRequestOptions(BaseModel):
    title: str
    body: Optional[str] = None
    head: str
    base: str
    maintainer_can_modify: Optional[bool] = None
    draft: Optional[bool] = None


class CreateBranchOptions(BaseModel):
    ref: str
    sha: str


class SearchRepositoriesParams(BaseModel):
    query: str
    page: Optional[int] = None
    per_page: Optional[int] = None


class ListCommitsParams(BaseModel):
    owner: str
    repo: str
    page: Optional[int] = None
    per_page: Optional[int] = None
    sha: Optional[str] = None


class ListIssuesOptions(BaseModel):
    owner: str
    repo: str
    state: Optional[Literal["open", "closed", "all"]] = None
    labels: Optional[List[str]] = None
    sort: Optional[Literal["created", "updated", "comments"]] = None
    direction: Optional[Literal["asc", "desc"]] = None
    since: Optional[str] = None
    page: Optional[int] = None
    per_page: Optional[int] = None


class UpdateIssueOptions(BaseModel):
    owner: str
    repo: str
    issue_number: int
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[Literal["open", "closed"]] = None
    labels: Optional[List[str]] = None
    assignees: Optional[List[str]] = None
    milestone: Optional[int] = None


class IssueComment(BaseModel):
    owner: str
    repo: str
    issue_number: int
    body: str


class GetIssueParams(BaseModel):
    owner: str
    repo: str
    issue_number: int


class GitHubForkParent(BaseModel):
    name: str
    full_name: str
    owner: GitHubOwner
    html_url: str


class GitHubFork(GitHubRepository):
    parent: GitHubForkParent
    source: GitHubForkParent


# Input Models
class ForkRepositoryParams(BaseModel):
    owner: str = Field(..., description="Repository owner (username or organization)")
    repo: str = Field(..., description="Repository name")
    organization: Optional[str] = Field(
        None,
        description="Optional: organization to fork to (defaults to your personal account)",
    )
