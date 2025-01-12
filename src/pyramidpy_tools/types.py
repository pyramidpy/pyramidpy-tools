from pydantic import BaseModel

class ApiKeyAuthConfig(BaseModel):
    api_key: str
