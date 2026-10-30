from github.client import Client
from github.issue import Issue


class Repo:

    def __init__(self, owner: str, name: str):
        self.owner = owner
        self.name = name
        self.client = Client()
        self.issues = self._fetch_issues()

    def _build_issue(self, item: dict) -> Issue:
        return Issue(
            owner=self.owner,
            name=self.name,
            number=item['number'],
            title=item['title'],
            body=item['body'] or '',
            timestamp=item['updated_at'],
            comments_count=item['comments'],
            client=self.client,
        )

    def _fetch_issues(self) -> list[Issue]:
        endpoint = f'repos/{self.owner}/{self.name}/issues'
        params = {'state': 'all', 'per_page': 100}
        issues: list[Issue] = []
        for items in self.client.paginate(endpoint, params=params):
            for item in items:
                if 'pull_request' in item:
                    continue
                issues.append(self._build_issue(item))
        return issues
