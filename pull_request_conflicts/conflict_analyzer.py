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

        self.ghtorrent_db = GHTorrentDB(pull_request_table_name=self.pull_request_table_name)

    def export_pull_request_conflict_table(self):
        filename = '{}_pull_request_conflict.csv'.format(self.project_name)

        pull_requests = self.ghtorrent_db.get_merged_pull_requests()

        pull_request_conflicts = self.analyze_pull_request_conflict(pull_requests)

        with open(filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['Pull Request ID', 'Amount of conflicting merges'])
            for pull_request_conflict in pull_request_conflicts:
                csv_writer.writerow(pull_request_conflict)

    def analyze_pull_request_conflict(self, pull_requests):
        pull_request_conflicts = []
        git = GitCommandLineInterface(repo_path=self.repo_path, repo_head=self.repo_head)
        for pull_request in pull_requests:
            merge_conflict_amount = 0
            # Buscar los commits que se hicieron durante la vida del PR
            pull_request_commits = self.ghtorrent_db.get_pull_requests_commits(pull_request)
            for pull_request_commit in pull_request_commits:
                commit_parents = self.ghtorrent_db.get_commit_parents(pull_request_commit.id)
                if len(commit_parents) > 1:
                    a_commit = commit_parents[0]
                    another_commit = commit_parents[1]
                    if git.conflicting_merge(a_commit.sha, another_commit.sha):
                        merge_conflict_amount += 1
            pull_request_conflicts.append([pull_request.pullreq_id, merge_conflict_amount])
        return pull_request_conflicts


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
            for another_pull_request in pull_requests:
                pull_request_pairwise_conflicts.append(
                    self.conflicting_pull_requests(a_pull_request, another_pull_request))
            pairwise_conflict_table.append(pull_request_pairwise_conflicts)
        return pairwise_conflict_table

    def conflicting_pull_requests(self, a_pull_request, another_pull_request):
        # Buscar las versiones a mergear de cada pull requests
        # luego tratar de mergearlas
        print("Merge entre PR #{} y PR #{}".format(a_pull_request.pullreq_id, another_pull_request.pullreq_id))

        #a_pull_request_commits = self.ghtorrent_db.get_pull_requests_commits(a_pull_request)
        #another_pull_request_commits = self.ghtorrent_db.get_pull_requests_commits(another_pull_request)

        a_pull_request_commit = self.ghtorrent_db.get_commit(a_pull_request.head_commit_id)
        another_pull_request_commit = self.ghtorrent_db.get_commit(another_pull_request.head_commit_id)

        #commit_date = min(a_pull_request_commits[-1].created_at, another_pull_request_commits[-1].created_at)

        #commit_sha_1 = filter(lambda c: c.created_at <= commit_date, a_pull_request_commits)[-1].sha
        #commit_sha_2 = filter(lambda c: c.created_at <= commit_date, a_pull_request_commits)[-1].sha

        # Quizas podamos filtrar por la fecha date_to del time window.

        # Aca tomo el ultimo commit
        #commit_sha_1 = a_pull_request_commits[-1].sha
        #commit_sha_2 = another_pull_request_commits[-1].sha

        # Aca tomo el primer commit del PR
        #commit_sha_1 = a_pull_request_commits[0].sha
        #commit_sha_2 = another_pull_request_commits[0].sha

        # Probemos con los heads de los PR
        commit_sha_1 = a_pull_request_commit.sha
        commit_sha_2 = another_pull_request_commit.sha

        print("Merge de commit {} en el commit {}".format(commit_sha_2, commit_sha_1))

        return int(self.git.conflicting_merge(commit_sha_1, commit_sha_2))
