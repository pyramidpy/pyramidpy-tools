import asyncio
import os
from github.GithubException import GithubException
from src.pyramidpy_tools.github.base import GitHubAPI
from src.pyramidpy_tools.github.schemas import (
    GitHubAuth,
    CreateRepositoryOptions,
    CreateBranchOptions,
    CreateIssueOptions,
    CreatePullRequestOptions,
    FileOperation,
)


async def github_flow_demo(collaborator_username: str = None):
    """
    Run the GitHub API flow demo testing all available functions.
    Args:
        collaborator_username: Optional GitHub username to add as collaborator.
                             If None, the collaborator steps will be skipped.
    """
    # Initialize GitHub API with your token
    github = GitHubAPI(GitHubAuth(token=os.getenv("GITHUB_TOKEN")))

    print("\n=== Repository Creation and Management ===")

    # 1. Create a new repository
    repo_options = CreateRepositoryOptions(
        name="demo-flow-repo",
        description="A demo repository to showcase GitHub API operations",
        private=False,
        auto_init=True,
        has_issues=True,
        has_wiki=True,
        has_downloads=True,
    )
    repo = await github.create_repository(repo_options)
    owner = repo.owner.login
    repo_name = repo.name
    print(f"Created repository: {owner}/{repo_name}")

    # 2. Search repositories
    search_results = await github.search_repositories(
        "language:python stars:>1000", page=1, per_page=5
    )
    print(f"Found {len(search_results)} popular Python repositories")

    # 3. Get and create branches
    default_branch = await github.get_default_branch(owner, repo_name)
    default_branch_sha = await github.get_default_branch_sha(owner, repo_name)
    print(f"Default branch: {default_branch}, SHA: {default_branch_sha}")

    feature_branch = "feature/new-feature"
    branch_options = CreateBranchOptions(ref=feature_branch, sha=default_branch_sha)
    await github.create_branch(owner, repo_name, branch_options)
    print(f"Created branch: {feature_branch}")

    # 4. List branches
    branches = await github.list_branches(owner, repo_name)
    print(f"Repository branches: {[branch.name for branch in branches]}")

    print("\n=== File Operations ===")

    # 5. Create and update files
    files = [
        FileOperation(
            path="README.md",
            content="# Demo Flow Repository\nThis repository demonstrates GitHub API operations.",
            operation="update",
        ),
        FileOperation(
            path="src/main.py",
            content="def main():\n    print('Hello, World!')\n\nif __name__ == '__main__':\n    main()",
            operation="create",
        ),
        FileOperation(
            path="src/utils.py",
            content="def helper():\n    return 'Helper function'",
            operation="create",
        ),
        FileOperation(
            path="tests/test_main.py",
            content="""import pytest
from src.main import main
from src.utils import helper

def test_helper():
    assert helper() == 'Helper function'

def test_main(capsys):
    main()
    captured = capsys.readouterr()
    assert captured.out == 'Hello, World!\\n'
""",
            operation="create",
        ),
        FileOperation(
            path="pyproject.toml",
            content="""[project]
name = "demo-flow-repo"
version = "1.0.0"
description = "A demo repository to showcase GitHub API operations"
requires-python = ">=3.9"

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "mypy>=1.0.0",
    "ruff>=0.1.0",
]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
addopts = "-v --cov=src --cov-report=term-missing"

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.ruff]
select = ["E", "F", "B", "I"]
line-length = 100""",
            operation="create",
        ),
        FileOperation(
            path=".github/workflows/pr_checks.yml",
            content="""name: PR Checks

on:
  pull_request:
    branches:
      - main
      - master

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11"]

    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
          
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install uv
          uv pip install -e ".[dev]"
          
      - name: Run linting
        run: |
          ruff check .
          ruff format --check .
          
      - name: Run type checking
        run: mypy src tests
        
      - name: Run tests
        run: |
          pytest tests/ -v --cov=src --cov-report=xml
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true

  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Bandit security checks
        uses: pypa/gh-action-bandit@release/v1
        with:
          python-version: "3.10"
          
      - name: Run dependency security scan
        uses: pypa/gh-action-pip-audit@v1.0.8
        with:
          inputs: requirements.txt

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
          
      - name: Build package
        run: |
          pip install build
          python -m build
          
      - name: Check package
        run: |
          pip install twine
          twine check dist/*""",
            operation="create",
        ),
    ]

    await github.push_files(
        owner, repo_name, feature_branch, files, "Add initial repository files"
    )
    print("Created/Updated repository files")

    # 6. Create/Update single file
    await github.create_or_update_file(
        owner,
        repo_name,
        "docs/README.md",
        "# Documentation\nThis folder contains project documentation.",
        "Add documentation README",
        feature_branch,
    )
    print("Created documentation README")

    print("\n=== Issue Management ===")

    # 7. Create and manage labels
    try:
        await github.create_label(
            owner,
            repo_name,
            name="bug",
            color="d73a4a",
            description="Something isn't working",
        )
        print("Created 'bug' label")
    except GithubException as e:
        if "already_exists" in str(e):
            print("'bug' label already exists")
        else:
            raise

    try:
        await github.create_label(
            owner,
            repo_name,
            name="enhancement",
            color="a2eeef",
            description="New feature or request",
        )
        print("Created 'enhancement' label")
    except GithubException as e:
        if "already_exists" in str(e):
            print("'enhancement' label already exists")
        else:
            raise

    # Create a custom label that shouldn't exist
    await github.create_label(
        owner,
        repo_name,
        name="custom-label",
        color="fbca04",
        description="A custom label for testing",
    )
    print("Created custom label")

    labels = await github.list_labels(owner, repo_name)
    print(f"Repository labels: {[label.name for label in labels]}")

    # 8. Create an issue
    issue_options = CreateIssueOptions(
        title="Implement new feature",
        body="We need to implement the new feature with the following requirements:\n\n- Requirement 1\n- Requirement 2",
        labels=["enhancement"],
    )
    issue = await github.create_issue(owner, repo_name, issue_options)
    print(f"Created issue #{issue.number}")

    # 9. Add comment to issue
    await github.add_issue_comment(
        owner, repo_name, issue.number, "I'll start working on this right away!"
    )
    print("Added comment to issue")

    # 10. List issues
    issues = await github.list_issues(owner, repo_name, state="open")
    print(f"Open issues: {len(issues)}")

    print("\n=== Collaboration ===")

    # 11. Manage collaborators
    if collaborator_username:
        try:
            await github.add_collaborator(
                owner, repo_name, collaborator_username, permission="write"
            )
            print(f"Added {collaborator_username} as collaborator")

            permissions = await github.get_repository_permissions(
                owner, repo_name, collaborator_username
            )
            print(f"Collaborator permissions: {permissions}")

            collaborators = await github.list_collaborators(owner, repo_name)
            print(
                f"Repository collaborators: {[collab.login for collab in collaborators]}"
            )
        except GithubException as e:
            print(f"Failed to manage collaborator: {e.data.get('message', str(e))}")

    print("\n=== Pull Request Management ===")

    # 12. Create a pull request
    pr_options = CreatePullRequestOptions(
        title="Feature: New Implementation",
        body="This PR implements the new feature.\n\nCloses #" + str(issue.number),
        head=feature_branch,
        base=default_branch,
    )
    pr = await github.create_pull_request(owner, repo_name, pr_options)
    print(f"Created pull request #{pr.number}")

    # 13. List and review pull request files
    pr_files = await github.list_pull_request_files(owner, repo_name, pr.number)
    print(f"Files changed in PR: {len(pr_files)}")

    if collaborator_username:
        await github.add_issue_comment(
            owner,
            repo_name,
            pr.number,
            f"@{collaborator_username} could you please review this PR?",
        )

    # 14. Compare commits
    comparison = await github.compare_commits(
        owner, repo_name, default_branch, feature_branch
    )
    commits_list = list(comparison.commits)
    print(f"Commits difference: {len(commits_list)} commits")

    # 15. Get specific commit
    if commits_list:
        commit = await github.get_commit(owner, repo_name, commits_list[0].sha)
        print(f"First commit author: {commit.commit.author.name}")
    else:
        print("No commits to compare")

    # 16. List commits
    commits = await github.list_commits(owner, repo_name)
    print(f"Repository commits: {len(commits)}")

    # 17. Merge pull request
    await github.merge_pull_request(
        owner,
        repo_name,
        pr.number,
        commit_title="Merge feature branch",
        commit_message="Merging new feature implementation",
        merge_method="squash",
    )
    print("Merged pull request")

    print("\n=== Repository Content Management ===")

    # 18. List directory contents
    contents = await github.list_directory_contents(owner, repo_name, "src")
    print("\nRepository contents:")
    for content in contents:
        print(f"\nFile: {content['path']}")
        print("Content:")
        print(content["decoded_content"])
        print("-" * 50)

    # 19. Delete file
    await github.delete_file(
        owner,
        repo_name,
        "docs/README.md",
        "Remove documentation README",
        branch=default_branch,
    )
    print("Deleted documentation README")

    print("\n=== Release Management ===")

    # 20. Create a release
    await github.create_release(
        owner,
        repo_name,
        tag="v1.0.0",
        name="Initial Release",
        body="First release of our demo repository",
        draft=False,
        prerelease=False,
    )
    print("Created release v1.0.0")

    # 21. List releases
    releases = await github.list_releases(owner, repo_name)
    print(f"Repository releases: {len(releases)}")

    # 22. Delete branch (cleanup)
    await github.delete_branch(owner, repo_name, feature_branch)
    print(f"Deleted branch: {feature_branch}")

    print("\nFlow completed successfully!")


if __name__ == "__main__":
    # You can provide a collaborator username as an environment variable
    collaborator = os.getenv("GITHUB_COLLABORATOR")
    asyncio.run(github_flow_demo(collaborator))
