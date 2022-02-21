# -*- coding: utf-8 -*-
from .ghtorrent import GHTorrentDB
from .github_api import GITHUBAPI


class GHTorrentUpdater(object):

    def __init__(self, project_name, repo_owner, repo_name):
        self.project_name = project_name
        self.pull_request_table_name = "{}_pull_requests".format(project_name)

        self.ghtorrent_db = GHTorrentDB(pull_request_table_name=self.pull_request_table_name)
        self.github = GITHUBAPI(owner=repo_owner, repo=repo_name)

    def fill_pull_request_base_branch(self):
        pull_requests = self.ghtorrent_db.get_pull_requests()
        pull_requests.reverse()
        for pull_request in pull_requests:
            if not pull_request.base_branch:
                print(pull_request.pullreq_id)
                pr_json = self.github.get_pull_request_info(pull_request.pullreq_id)
                base_branch = pr_json and pr_json.get('base') and pr_json.get('base').get('label') or ''
                print(base_branch)
                pull_request.base_branch = base_branch
                self.ghtorrent_db.set_pull_request_base_branch(pull_request)