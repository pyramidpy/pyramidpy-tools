"""
File system tools for file operations
"""

from controlflow.tools.tools import tool

from pyramidpy_tools.toolkit import Toolkit

from .base import FileStorage


@tool(
    name="save_file_content",
    description="Save file content to the file system",
)
def save_file_content(file_content: str, path: str):
    file = FileStorage().save_file_content(file_content.encode(), path)
    return f"File saved with ID: {file.id}"


@tool(
    name="download_file",
    description="Download file content from the file system",
)
def download_file(file_id: str):
    try:
        file_content = FileStorage().download_file(file_id)
        return file_content.decode()
    except FileNotFoundError as e:
        return str(e)


@tool(
    name="list_files",
    description="List files in the file system",
)
def list_files():
    files = FileStorage().list_files()
    return [
        {
            "id": file.id,
            "filename": file.filename,
            "original_filename": file.original_filename,
            "content_type": file.content_type,
            "file_size": file.file_size,
            "created_at": file.created_at.isoformat(),
            "updated_at": file.updated_at.isoformat(),
        }
        for file in files
    ]


@tool(
    name="delete_file",
    description="Delete file from the file system",
)
def delete_file(file_id: str):
    FileStorage().delete_file(file_id)
    return f"File {file_id} deleted"


file_system_toolkit = Toolkit.create_toolkit(
    id="file_system_toolkit",
    tools=[save_file_content, download_file, list_files, delete_file],
    description="Tools for file system operations",
    name="file_system_toolkit",
)
