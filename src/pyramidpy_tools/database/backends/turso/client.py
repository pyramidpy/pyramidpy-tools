import httpx
import humps

from pyramidpy_tools.settings import settings


class TursoClient:
    timeout = 140
    base_url = "https://api.turso.tech"

    def __init__(self, api_key: str | None = None):
        if api_key is None:
            api_key = settings.TURSO_AUTH_TOKEN
        self.api_key = api_key

    def get(self, url: str, **kwargs):
        url = self.base_url + url
        headers = {"Authorization": f"Bearer {self.api_key}"}
        r = httpx.get(url, **kwargs, timeout=self.timeout, headers=headers)
        r.raise_for_status()
        return humps.decamelize(r.json())

    def post(self, url: str, **kwargs):
        url = self.base_url + url
        headers = {"Authorization": f"Bearer {self.api_key}"}

        r = httpx.post(url, **kwargs, timeout=self.timeout, headers=headers)
        r.raise_for_status()
        return humps.decamelize(r.json())

    def delete(self, url: str, **kwargs):
        url = self.base_url + url
        headers = {"Authorization": f"Bearer {self.api_key}"}
        r = httpx.delete(url, **kwargs, timeout=self.timeout, headers=headers)
        r.raise_for_status()
        return humps.decamelize(r.json())
