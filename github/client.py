from collections.abc import Iterator
from os import environ
from pathlib import Path
import time

from dotenv import load_dotenv
import requests


class Client:

    def __init__(self):
        self.base_url = 'https://api.github.com'
        load_dotenv(Path(environ['BUILD_WORKING_DIRECTORY']) / '.env')
        token = environ['GITHUB_TOKEN']
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/vnd.github+json',
            'Authorization': f'Bearer {token}',
            'X-GitHub-Api-Version': '2022-11-28',
        })

    def get(
        self, endpoint: str, params: dict | None = None
    ) -> list[dict] | dict:
        return self._request(endpoint, params=params).json()

    def paginate(
        self, endpoint: str, params: dict | None = None
    ) -> Iterator[list[dict]]:
        next_endpoint: str | None = endpoint
        next_params = params
        while next_endpoint is not None:
            response = self._request(next_endpoint, params=next_params)
            yield response.json()
            next_endpoint = response.links.get('next', {}).get('url')
            next_params = None

    def _request(
        self, endpoint: str, params: dict | None = None
    ) -> requests.Response:
        url = self._url(endpoint)
        while True:
            response = self.session.get(url, params=params, timeout=30)
            delay = self._retry_delay(response)
            if delay is not None:
                print(
                    f'GitHub rate limit hit; sleeping {delay}s...', flush=True
                )
                time.sleep(delay)
                continue
            response.raise_for_status()
            return response

    def _url(self, endpoint: str) -> str:
        if endpoint.startswith('https://'):
            return endpoint
        path = endpoint.lstrip('/')
        return f'{self.base_url}/{path}'

    def _retry_delay(self, response: requests.Response) -> int | None:
        if response.status_code not in (403, 429):
            return None
        if 'Retry-After' in response.headers:
            return int(response.headers['Retry-After']) + 1
        if response.headers.get('X-RateLimit-Remaining') == '0':
            reset = int(response.headers['X-RateLimit-Reset'])
            seconds_until_reset = reset - int(time.time()) + 1
            return max(1, seconds_until_reset)
        return None
