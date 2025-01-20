# GitHub Flow

## Example flow

```python
import controlflow as cf
from typing import List, Dict, Any

# Planning Agent - The orchestrator
planner = cf.Agent(
    name="WorkflowPlanner",
    description="A strategic AI agent that plans and coordinates GitHub workflow tasks",
    instructions="""
        You are responsible for:
        - Analyzing user objectives
        - Breaking down objectives into concrete tasks
        - Assigning tasks to appropriate specialized agents
        - Determining task dependencies and order
        - Ensuring the overall workflow achieves the objective
        
        Consider:
        1. Required GitHub API operations
        2. Logical task sequencing
        3. Data dependencies between tasks
        4. Error handling and validation steps
        """
)

# Specialized Agents (from previous implementation)
specialized_agents = {
    "file_ops": cf.Agent(
        name="FileManager",
        description="Handles file operations in GitHub repositories",
        instructions="Manage file creation, updates, deletions, and content management."
    ),
    "pr_ops": cf.Agent(
        name="PRManager",
        description="Manages pull request operations",
        instructions="Handle PR creation, reviews, merges, and related operations."
    ),
    "issue_ops": cf.Agent(
        name="IssueManager",
        description="Manages GitHub issues",
        instructions="Handle issue creation, updates, labels, and tracking."
    ),
    "repo_ops": cf.Agent(
        name="RepoManager",
        description="Manages repository operations",
        instructions="Handle repository configuration, branches, and settings."
    )
}

def create_dynamic_task(task_spec: Dict[str, Any]) -> cf.Task:
    """Helper function to create a task from a specification"""
    return cf.Task(
        description=task_spec["description"],
        agents=[specialized_agents[task_spec["agent"]]],
        context=task_spec.get("context", {}),
        depends_on=task_spec.get("depends_on", []),
        result_type=task_spec.get("result_type", Any)
    )

@cf.flow
def plan_github_workflow(objective: str, context: Dict[str, Any] = None) -> List[cf.Task]:
    """
    Plan and create a dynamic workflow based on the objective
    """
    # Planning task to analyze objective and create task specifications
    planning_task = cf.Task(
        f"Plan workflow for objective: {objective}",
        agents=[planner],
        context={"objective": objective, "available_agents": list(specialized_agents.keys())},
        result_type=List[Dict[str, Any]]
    )
    
    # Get the task specifications from the planner
    task_specs = planning_task.run()
    
    # Create tasks based on the plan
    tasks = []
    task_map = {}
    
    for spec in task_specs:
        # Replace dependency references with actual task objects
        if "depends_on" in spec:
            spec["depends_on"] = [task_map[dep_id] for dep_id in spec["depends_on"]]
        
        # Create the task
        task = create_dynamic_task(spec)
        tasks.append(task)
        task_map[spec["id"]] = task
    
    return tasks

def execute_github_workflow(
    objective: str,
    owner: str,
    repo: str,
    **additional_context
) -> Dict[str, Any]:
    """
    Execute a dynamic GitHub workflow based on the objective
    """
    # Prepare context
    context = {
        "owner": owner,
        "repo": repo,
        **additional_context
    }
    
    # Plan the workflow
    tasks = plan_github_workflow(objective, context)
    
    # Execute all tasks
    results = {}
    for task in tasks:
        result = task.run()
        results[task.description] = result
    
    return results

# Example usage:
if __name__ == "__main__":
    # Example 1: Simple file update workflow
    result1 = execute_github_workflow(
        objective="Update README.md with new project description and create a PR",
        owner="username",
        repo="repo-name",
        file_path="README.md",
        new_content="# Updated Project\nNew description here..."
    )
    
    # Example 2: Complex issue management workflow
    result2 = execute_github_workflow(
        objective="Analyze all open issues, add labels based on content, and assign to team members",
        owner="username",
        repo="repo-name",
        label_rules={
            "bug": ["error", "crash", "fix"],
            "enhancement": ["improve", "feature", "add"],
            "documentation": ["docs", "explain", "clarify"]
        },
        team_members=["alice", "bob", "charlie"]
    )
```
