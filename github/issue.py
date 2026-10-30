import json
import os
from pathlib import Path

from github.client import Client
from github.comment import Comment


class Issue:

    def __init__(
        self,
        owner: str,
        name: str,
        number: int,
        title: str,
        body: str,
        timestamp: str,
        comments_count: int,
        client: Client,
    ):
        self.owner = owner
        self.name = name
        self.number = number
        self.title = title
        self.body = body
        self.timestamp = timestamp
        self.url = (
            f'https://github.com/{self.owner}/{self.name}/issues/{self.number}'
        )
        self.client = client
        self.path = (
            Path(os.environ['BUILD_WORKING_DIRECTORY'])
            / 'data'
            / 'github'
            / self.owner
            / self.name
            / 'issues'
            / f'{self.number}.json'
        )
        self.previous = self._load_previous()
        if self._is_stale():
            print(f'Fetching: {self.url}', flush=True)
            self.comments = (
                self._fetch_comments() if comments_count > 0 else []
            )
            self._save()
        else:
            self._load()

    def _load_previous(self) -> dict | None:
        if not self.path.exists():
            return None
        return json.loads(self.path.read_text())

    def _is_stale(self) -> bool:
        # GitHub bumps the issue-level timestamp on any activity in the issue
        # (body edits, state changes, new or edited comments), so an unchanged
        # timestamp means nothing in the issue changed.
        if self.previous is None:
            return True
        return self.previous['timestamp'] != self.timestamp

    def _load(self) -> None:
        self.title = self.previous['title']
        self.body = self.previous['body']
        self.comments = [
            Comment(
                id=item['id'],
                body=item['body'],
                timestamp=item['timestamp'],
            )
            for item in self.previous['comments']
        ]

    def _fetch_comments(self) -> list[Comment]:
        endpoint = f'repos/{self.owner}/{self.name}/issues/{self.number}/comments'
        params = {'per_page': 100}
        comments: list[Comment] = []
        for items in self.client.paginate(endpoint, params=params):
            for item in items:
                comments.append(
                    Comment(
                        id=item['id'],
                        body=item['body'] or '',
                        timestamp=item['updated_at'],
                    )
                )
        return comments

    def to_dict(self) -> dict:
        return {
            'title': self.title,
            'body': self.body,
            'timestamp': self.timestamp,
            'url': self.url,
            'comments': [comment.to_dict() for comment in self.comments],
        }

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.to_dict(), indent=2))
