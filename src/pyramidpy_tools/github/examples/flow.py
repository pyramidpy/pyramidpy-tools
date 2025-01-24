import controlflow as cf
from prefect.settings import PREFECT_API_KEY, PREFECT_API_URL, temporary_settings
import os

# File Management Agents
file_manager = cf.Agent(
    name="FileManager",
    description="An AI agent that handles file operations in GitHub repositories",
    instructions="""
        You are responsible for:
        - Creating and updating files
        - Managing directory contents
        - Handling file deletions
        - Ensuring file content is properly formatted
        Always verify file operations and provide clear status updates.
        """,
)

content_reviewer = cf.Agent(
    name="ContentReviewer",
    description="An AI agent that reviews content changes and file modifications",
    instructions="""
        Your role is to:
        - Review file changes for quality and correctness
        - Verify content meets repository standards
        - Suggest improvements to file content
        - Ensure documentation is clear and complete
        Be thorough in reviews and provide constructive feedback.
        """,
)

# PR Management Agents
pr_manager = cf.Agent(
    name="PRManager",
    description="An AI agent that manages pull request operations",
    instructions="""
        You handle:
        - Creating and updating pull requests
        - Managing PR reviews and comments
        - Coordinating PR merges
        - Ensuring PR quality standards
        Maintain high standards for code quality and documentation.
        """,
)

pr_reviewer = cf.Agent(
    name="PRReviewer",
    description="An AI agent that reviews pull requests",
    instructions="""
        Your responsibilities include:
        - Reviewing PR changes thoroughly
        - Providing detailed feedback
        - Checking for conflicts
        - Ensuring PR meets contribution guidelines
        Be strict but constructive in reviews.
        """,
)

# Issue Management Agents
issue_manager = cf.Agent(
    name="IssueManager",
    description="An AI agent that manages GitHub issues",
    instructions="""
        You are responsible for:
        - Creating and updating issues
        - Managing issue labels
        - Coordinating issue assignments
        - Tracking issue status
        Ensure clear communication and proper categorization.
        """,
)

issue_reviewer = cf.Agent(
    name="IssueReviewer",
    description="An AI agent that reviews and triages issues",
    instructions="""
        Your role is to:
        - Review issue content and validity
        - Prioritize issues
        - Suggest issue improvements
        - Ensure issues are properly documented
        Maintain high quality standards for issue tracking.
        """,
)

# Repository Management Agents
repo_manager = cf.Agent(
    name="RepoManager",
    description="An AI agent that manages repository-level operations",
    instructions="""
        You handle:
        - Repository settings and configuration
        - Branch management
        - Release management
        - Collaborator access
        Ensure repository maintenance and security.
        """,
)


def github_workflow(owner: str, repo: str, branch: str):
    # Repository Setup Tasks
    repo_setup_task = cf.Task(
        "Verify repository setup and configuration",
        agents=[repo_manager],
        context={"owner": owner, "repo": repo},
    )
    # File Management Tasks
    file_creation_task = cf.Task(
        "Create and update repository files",
        agents=[file_manager],
        context={"repo_setup": repo_setup_task},
        depends_on=[repo_setup_task],
    )
    content_review_task = cf.Task(
        "Review file contents and structure",
        agents=[content_reviewer],
        context={"file_changes": file_creation_task},
        depends_on=[file_creation_task],
    )
    # Issue Management Tasks
    issue_creation_task = cf.Task(
        "Create and configure issues",
        agents=[issue_manager],
        context={"repo_setup": repo_setup_task},
    )
    issue_review_task = cf.Task(
        "Review and triage issues",
        agents=[issue_reviewer],
        context={"issues": issue_creation_task},
        depends_on=[issue_creation_task],
    )
    # PR Management Tasks
    pr_creation_task = cf.Task(
        "Create and configure pull request",
        agents=[pr_manager],
        context={"file_changes": content_review_task, "branch": branch},
        depends_on=[content_review_task],
    )
    pr_review_task = cf.Task(
        "Review pull request changes",
        agents=[pr_reviewer],
        context={"pull_request": pr_creation_task},
        depends_on=[pr_creation_task],
    )

    # Final Repository Tasks
    repo_finalization_task = cf.Task(
        "Finalize repository changes and updates",
        agents=[repo_manager],
        context={"pr_status": pr_review_task, "issue_status": issue_review_task},
        depends_on=[pr_review_task, issue_review_task],
    )

    tasks = [
        repo_setup_task,
        file_creation_task,
        content_review_task,
        issue_creation_task,
        issue_review_task,
        pr_creation_task,
        pr_review_task,
        repo_finalization_task,
    ]
    return tasks


if __name__ == "__main__":
    with temporary_settings(
        set_defaults={
            PREFECT_API_KEY: os.getenv("PREFECT_API_KEY"),
            PREFECT_API_URL: os.getenv("PREFECT_API_URL"),
        }
    ):
        print("Starting GitHub Workflow")
        result = github_workflow(
            owner="kuerbis-h", repo="agentic-tools-demo", branch="main"
        )

        print(result)
        flow_results = []
        with cf.Flow() as flow:
            for event in cf.run_tasks(result):
                flow_results.append(event)
        print(flow_results)
