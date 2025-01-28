import tempfile
import boto3
from botocore.exceptions import ClientError
import io
from pyramidpy_tools import settings
from .schemas import BucketConfig


class StorageS3Client:
    """
    # Usage example:
    # tigris = StorageS3Client()
    # tigris.upload_file('local_file.txt', 'remote_file.txt')
    # tigris.download_file('remote_file.txt', 'downloaded_file.txt')
    # presigned_url = tigris.generate_presigned_url('remote_file.txt', expiration=3600, http_method='get')
    # object_list = tigris.list_objects()

    """

    def __init__(self, config: BucketConfig = None):
        self.s3_client = boto3.client(
            "s3",
            endpoint_url=config.aws_endpoint_url_s3 or settings.storage.s3_endpoint_url,
            region_name=config.aws_region or settings.storage.s3_region,
            aws_access_key_id=config.aws_access_key_id
            or settings.storage.s3_access_key,
            aws_secret_access_key=config.aws_secret_access_key
            or settings.storage.s3_secret_key,
        )
        self.bucket_name = config.bucket_name

    def exists(self, object_name):
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError:
            return False

    def upload_file(self, file_object: io.BytesIO, file_name):
        try:
            # check if open
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(file_object.read())
            self.s3_client.upload_file(temp_file.name, self.bucket_name, file_name)
            return True
        except ClientError:
            return False

    def download_file(self, object_name, file_path):
        try:
            local_file_path = file_path.split("/")[-1]
            with open(local_file_path, "wb") as f:
                self.s3_client.download_fileobj(self.bucket_name, object_name, f)
                return local_file_path
        except ClientError:
            return None

    def generate_presigned_url(
        self,
        object_name,
        expiration=3600 * 24,  # valid for 1 hour
        http_method="get",
        content_type=None,
        as_attachment=True,
    ):
        try:
            params = {
                "Bucket": self.bucket_name,
                "Key": object_name,
            }
            http_method = http_method or "get"
            if content_type:
                params["ResponseContentType"] = content_type
            if not as_attachment:
                params["ResponseContentDisposition"] = "inline"

            url = self.s3_client.generate_presigned_url(
                f"{http_method}_object", Params=params, ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating presigned URL: {e}")
            return None

    def list_objects(self, prefix=""):
        try:
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )
            return [obj["Key"] for obj in response.get("Contents", [])]
        except ClientError as e:
            print(f"Error listing objects: {e}")
            return []

    def delete_object(self, object_name):
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"Error deleting object: {e}")
            return False

    def generate_streaming_url(self, object_name, expiration=3600):
        try:
            params = {
                "Bucket": self.bucket_name,
                "Key": object_name,
                "ResponseContentType": "audio/mpeg",  # Adjust based on your file type
                "ResponseContentDisposition": "inline",
            }

            url = self.s3_client.generate_presigned_url(
                "get_object", Params=params, ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            print(f"Error generating streaming URL: {e}")
            return None

    def stream_to_file(self, object_name, chunk_iterator):
        try:
            # Initiate multipart upload
            mpu = self.s3_client.create_multipart_upload(
                Bucket=self.bucket_name, Key=object_name
            )
            upload_id = mpu["UploadId"]

            parts = []
            part_number = 1

            for chunk in chunk_iterator:
                # Upload part
                part = self.s3_client.upload_part(
                    Body=chunk,
                    Bucket=self.bucket_name,
                    Key=object_name,
                    PartNumber=part_number,
                    UploadId=upload_id,
                )

                parts.append({"PartNumber": part_number, "ETag": part["ETag"]})

                part_number += 1

            # Complete multipart upload
            self.s3_client.complete_multipart_upload(
                Bucket=self.bucket_name,
                Key=object_name,
                UploadId=upload_id,
                MultipartUpload={"Parts": parts},
            )

            print(f"File streamed successfully to {self.bucket_name}/{object_name}")
            return True

        except Exception:
            # Abort the multipart upload if it was initiated
            if "upload_id" in locals():
                self.s3_client.abort_multipart_upload(
                    Bucket=self.bucket_name, Key=object_name, UploadId=upload_id
                )
            return False

    def generate_public_url(self, bytes_object: bytes, file_name: str):
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name, Key=file_name, Body=bytes_object
            )
            return True
        except ClientError:
            return False
