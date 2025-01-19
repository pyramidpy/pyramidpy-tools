from controlflow.tools.tools import tool


@tool(
    name="user_tool",
    description="The user can only see the messages you send to them.",
    instructions="""
    Use this tool to communicate with the user. 
    You can send the messages and they will respond asynchronously.
    NB! The user can only see messages sent using this tool. ALL other messages are not visible.
    """,
)
async def user_tool(message: str):
    return """
        Message sent to user. 
        If the task is done you can mark it as complete, otherwise proceed with other tasks.
    """
