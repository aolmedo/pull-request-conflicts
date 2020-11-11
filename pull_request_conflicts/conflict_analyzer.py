# -*- coding: utf-8 -*-
from ghtorrent import GHTorrentDB
from git_cmd import GitCommandLineInterface


class PullRequestConflcitAnalyzer(object):
    """
        class
    """

    def __init__(self, project_name, repo_path, repo_head=None):
        self.project_name = project_name
        self.repo_path = repo_path
        self.repo_head = repo_head if repo_head else 'master'
        self.pull_request_table_name = "{}_pull_requests".format(project_name)

    def analyze(self):
        ghtorrent_db = GHTorrentDB(pull_request_table_name=self.pull_request_table_name)
        git = GitCommandLineInterface(repo_path=self.repo_path, repo_head=self.repo_head)

        pull_requests = ghtorrent_db.get_pull_requests()

        for pull_request in pull_requests:
            merge_conflict_amount = 0
            conflicting_merge = False
            # Buscar los commits que se hicieron durante la vida del PR
            pull_request_commits = ghtorrent_db.get_pull_requests_commits(pull_request)
            for pull_request_commit in pull_request_commits:
                commit_parents = ghtorrent_db.get_commit_parents(pull_request_commit.id)
                if len(commit_parents) > 1:
                    a_commit = commit_parents[0]
                    another_commit = commit_parents[1]
                    if git.conflicting_merge(a_commit.sha, another_commit.sha):
                        conflicting_merge = True
                        merge_conflict_amount += 1

            if conflicting_merge:
                ghtorrent_db.set_pull_request_conflicting_merge(pull_request)
                ghtorrent_db.set_pull_request_merge_conflict_amount(pull_request, merge_conflict_amount)
