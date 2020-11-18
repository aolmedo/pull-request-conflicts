# -*- coding: utf-8 -*-
import datetime
import csv
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

        pull_requests = ghtorrent_db.get_merged_pull_requests()

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


class PairwiseConflictAnalyzer(object):
    """
    """

    def __init__(self, project_name, repo_path, repo_head=None):
        self.project_name = project_name
        self.repo_path = repo_path
        self.repo_head = repo_head if repo_head else 'master'
        self.pull_request_table_name = "{}_pull_requests".format(project_name)

        self.ghtorrent_db = GHTorrentDB(pull_request_table_name=self.pull_request_table_name)
        self.git = GitCommandLineInterface(repo_path=self.repo_path, repo_head=self.repo_head)

    def export_pairwise_conflict_table(self, date_from, date_to):
        date_from_str = date_from.strftime('%Y%m%d')
        date_to_str = date_to.strftime('%Y%m%d')
        filename = '{}_pairwise_conflict_{}_{}.csv'.format(self.project_name,
                                                           date_from_str, date_to_str)

        pull_requests = self.ghtorrent_db.get_pull_requests_between(date_from, date_to)
        pairwise_conflict_table = self.calculate_pairwise_conflict_table(pull_requests)
        with open(filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([''] + [pr.pullreq_id for pr in pull_requests])
            for i, pr_row in enumerate(pairwise_conflict_table):
                csv_writer.writerow([pull_requests[i].pullreq_id] + pr_row)

    def calculate_pairwise_conflict_table(self, pull_requests):
        pairwise_conflict_table = []

        for a_pull_request in pull_requests:
            pull_request_pairwise_conflicts = []
            for another_pull_requests in pull_requests:
                pull_request_pairwise_conflicts.append(
                    self.conflicting_pull_requests(a_pull_request, another_pull_request))
            pairwise_conflict_table.append(pull_request_pairwise_conflicts)
        return pairwise_conflict_table

    def conflicting_pull_requests(self, a_pull_request, another_pull_request):
        # Buscar las versiones a mergear de cada pull requests
        # luego tratar de mergearlas
        a_pull_request_commits = self.ghtorrent_db.get_pull_requests_commits(a_pull_request)
        another_pull_request_commits = self.ghtorrent_db.get_pull_requests_commits(another_pull_request)

        commit_date = min(a_pull_request_commits[-1].created_at, another_pull_request_commits[-1].created_at)

        commit_sha_1 = filter(lambda c: c.created_at <= commit_date, a_pull_request_commits)[-1].sha
        commit_sha_2 = filter(lambda c: c.created_at <= commit_date, a_pull_request_commits)[-1].sha
        return int(self.git.conflicting_merge(commit_sha_1, commit_sha_2))
