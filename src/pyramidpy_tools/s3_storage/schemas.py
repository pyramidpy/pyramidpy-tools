from pydantic import BaseModel


class BucketConfig(BaseModel):
    bucket_name: str
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_endpoint_url_s3: str
    aws_region: str
    location: str = "private"
    default_acl: str = "private"
    file_overwrite: bool = False
