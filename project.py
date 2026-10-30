import json
import os
from pathlib import Path


class Project:

    def __init__(self):
        path = Path(os.environ['BUILD_WORKING_DIRECTORY']) / 'project.json'
        data = json.loads(path.read_text())
        self.repos = []
        for repo in data.get('github', []):
            owner = repo['owner']
            name = repo['name']
            self.repos.append(Repo(owner, name))
