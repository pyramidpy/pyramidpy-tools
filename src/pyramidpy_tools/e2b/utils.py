"""
Utility functions for E2B code execution
"""

import base64
import io
import uuid
from typing import Tuple, List, Dict, Any

import rich
from e2b_code_interpreter import Result

from pyramidpy_tools.s3_storage.base import StorageS3Client
from pyramidpy_tools.s3_storage.schemas import BucketConfig
from pyramidpy_tools.settings import settings


async def save_file_to_storage(
    file_data: bytes,
    file_name: str,
    storage_client: StorageS3Client,
) -> str:
    """
    Save file data to S3 storage and return the URL

    Args:
        file_data: Raw file data to save
        file_name: Name to save the file as
        storage_client: Configured S3 storage client

    Returns:
        str: URL to access the saved file
    """
    file_obj = io.BytesIO(file_data)
    file_obj.seek(0)

    if storage_client.upload_file(file_obj, file_name):
        return storage_client.generate_presigned_url(
            file_name,
            expiration=3600 * 24,  # 24 hours
            as_attachment=False,
        )
    return None


async def handle_execution_result(
    result: Result, storage_config: BucketConfig | None = None
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Process execution results and save any generated files

    Args:
        result: The execution result to process
        storage_config: S3 storage configuration

    Returns:
        Tuple containing:
        - List of file URLs
        - List of data sources
    """
    files = []
    data_sources = []
    file_results = ["png", "jpeg", "pdf", "svg", "latex", "json", "javascript"]

    if not storage_config:
        storage_config = BucketConfig(
            bucket_name=settings.storage.s3_bucket,
            aws_access_key_id=settings.storage.s3_access_key,
            aws_secret_access_key=settings.storage.s3_secret_key,
            aws_region=settings.storage.s3_region,
            aws_endpoint_url_s3=settings.storage.s3_endpoint_url,
        )
    storage_client = StorageS3Client(storage_config)

    for file_type in file_results:
        if result[file_type]:
            try:
                file_id = str(uuid.uuid4())[0:8]
                data = base64.b64decode(result[file_type])
                file_name = f"{file_id}-{file_type}.{file_type}"

                file_url = await save_file_to_storage(data, file_name, storage_client)
                if file_url:
                    files.append(file_url)
                    # Add to data sources if it's a visualization or data file
                    if file_type in ["png", "jpeg", "svg", "json"]:
                        data_sources.append(
                            {"type": file_type, "url": file_url, "id": file_id}
                        )
            except Exception as e:
                rich.print(f"Error saving {file_type} output: {e}")

    # Log other outputs
    if result.text:
        rich.print(f"Text output: {result.text}")
    if result.markdown:
        rich.print(f"Markdown output: {result.markdown}")
    if result.html:
        rich.print(f"HTML output: {result.html}")
    if result.extra:
        rich.print(f"Extra output: {result.extra}")

    return files, data_sources


def log_stream(stream):
    """Log output stream from code execution"""
    for line in stream:
        rich.print(f"[Code Interpreter stdout] {line}")
