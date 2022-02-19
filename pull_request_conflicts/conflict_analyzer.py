# -*- coding: utf-8 -*-
import datetime
import subprocess
import csv
import re
from . import settings
from .ghtorrent import GHTorrentDB
from .git_cmd import GitCommandLineInterface


class PullRequestConflictAnalyzer(object):
    """
        Analiza cuantos conflictos tuvo cada PR
    """

    def __init__(self, project_name, repo_path=None, repo_head=None):
        self.project_name = project_name
        self.repo_path = repo_path if repo_path else ''
        self.repo_head = repo_head if repo_head else 'master'
        self.pull_request_table_name = "{}_pull_requests".format(project_name)
        self.data_path = settings.DATA_PATH
        self.base_filename = 'pull_request_conflict'

        self.ghtorrent_db = GHTorrentDB(pull_request_table_name=self.pull_request_table_name)
        self.git = GitCommandLineInterface(repo_path=self.repo_path, repo_head=self.repo_head)

    def get_conflict_by_pull_requests(self):
        filename = '{}/{}_{}.csv'.format(self.data_path, self.project_name, self.base_filename)

        pull_request_conflicts = {}

        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                pr_key = row[0]
                pr_value = int(row[1])
                pull_request_conflicts[pr_key] = pr_value

        return pull_request_conflicts

    def export_pull_request_conflict_table(self, date_from, date_to):
        date_from_str = date_from.strftime('%Y%m%d')
        date_to_str = date_to.strftime('%Y%m%d')
        filename = '{}/{}_{}_{}_{}.csv'.format(self.data_path, self.project_name,
                                               self.base_filename, date_from_str, date_to_str)

        pull_requests = self.ghtorrent_db.get_merged_pull_requests_between(date_from, date_to)

        pull_request_conflicts = self.analyze_pull_request_conflict(pull_requests)

        with open(filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            # csv_writer.writerow(['Pull Request ID', 'Amount of conflicting merges'])
            for pull_request_conflict in pull_request_conflicts:
                csv_writer.writerow(pull_request_conflict)

    def analyze_pull_request_conflict(self, pull_requests):
        pull_request_conflicts = []
        
        for pull_request in pull_requests:
            # Buscar los commits que se hicieron durante la vida del PR
            pull_request_commits = self.ghtorrent_db.get_pull_requests_commits(pull_request)
            inner_merge_conflict_amount = self.get_inner_conflict_amount(pull_request_commits)
            outer_merge_conflict_amount = self.get_outer_conflict_amount(pull_request_commits)
            merge_conflict_amount = inner_merge_conflict_amount + outer_merge_conflict_amount
            pull_request_conflicts.append([pull_request.pullreq_id, merge_conflict_amount])
        return pull_request_conflicts

    def get_inner_conflict_amount(self, pull_request_commits):
        merge_conflict_amount = 0
        for pull_request_commit in pull_request_commits:
            commit_parents = self.ghtorrent_db.get_commit_parents(pull_request_commit.id)
            if len(commit_parents) > 1:
                a_commit = commit_parents[0]
                another_commit = commit_parents[1]
                if self.git.conflicting_merge(a_commit.sha, another_commit.sha):
                    merge_conflict_amount += 1
        return merge_conflict_amount

    def get_outer_conflict_amount(self, pull_request_commits):
        merge_conflict_amount = 0
        for pull_request_commit in pull_request_commits:
            commit_children = self.ghtorrent_db.get_commit_children(pull_request_commit.id)
            for commit_child in commit_children:
                commit_child_parents = self.ghtorrent_db.get_commit_parents(commit_child.id)
                if len(commit_child_parents) > 1:
                    a_commit = commit_child_parents[0]
                    another_commit = commit_child_parents[1]
                    if self.git.conflicting_merge(a_commit.sha, another_commit.sha):
                        merge_conflict_amount += 1
        return merge_conflict_amount


class PairwiseConflictAnalyzer(object):
    """
    """

    def __init__(self, project_name, repo_path=None, repo_head=None):
        self.project_name = project_name
        self.repo_path = repo_path if repo_path else ''
        self.repo_head = repo_head if repo_head else 'master'
        self.pull_request_table_name = "{}_pull_requests".format(project_name)
        self.data_path = settings.DATA_PATH
        self.base_filename = 'pairwise_conflict_by_pull_request'

        self.ghtorrent_db = GHTorrentDB(pull_request_table_name=self.pull_request_table_name)
        self.git = GitCommandLineInterface(repo_path=self.repo_path, repo_head=self.repo_head)

    def get_pairwise_conflict_by_pull_request(self):
        filename = '{}/{}_{}.csv'.format(self.data_path, self.project_name, self.base_filename)

        pairwise_conflict_by_pull_request = {}

        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                pr_key = row[0]
                if row[1]:
                    pr_value = row[1].split(',')
                else:
                    pr_value = []
                pairwise_conflict_by_pull_request[pr_key] = pr_value

        return pairwise_conflict_by_pull_request

    def export_pairwise_conflict_table(self, date_from, date_to):
        date_from_str = date_from.strftime('%Y%m%d')
        date_to_str = date_to.strftime('%Y%m%d')
        filename = '{}_pairwise_conflict_{}_{}.csv'.format(self.project_name,
                                                           date_from_str, date_to_str)

        pull_requests = self.ghtorrent_db.get_merged_pull_requests_between(date_from, date_to)
        pairwise_conflict_table = self.calculate_pairwise_conflict_table(pull_requests)
        with open(filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow([''] + [pr.pullreq_id for pr in pull_requests])
            for i, pr_row in enumerate(pairwise_conflict_table):
                csv_writer.writerow([pull_requests[i].pullreq_id] + pr_row)

    def export_pairwise_conflict_by_pull_request(self, date_from, date_to):
        date_from_str = date_from.strftime('%Y%m%d')
        date_to_str = date_to.strftime('%Y%m%d')
        filename = '{}_pairwise_conflict_by_pull_request_{}_{}.csv'.format(self.project_name,
                                                                           date_from_str, date_to_str)

        pull_requests = self.ghtorrent_db.get_merged_pull_requests_between(date_from, date_to)
        pairwise_conflict_by_pull_request = self.calculate_pull_request_pairwise_conflicts(pull_requests)
        with open(filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            for k, v in pairwise_conflict_by_pull_request.items():
                prs = ','.join(v)
                csv_writer.writerow([k, prs])

    def calculate_pairwise_conflict_table(self, pull_requests):
        pairwise_conflict_table = []

        for a_pull_request in pull_requests:
            pull_request_pairwise_conflicts = []
            for another_pull_request in pull_requests:
                pull_request_pairwise_conflicts.append(
                    self.conflicting_pull_requests(a_pull_request, another_pull_request))
            pairwise_conflict_table.append(pull_request_pairwise_conflicts)
        return pairwise_conflict_table

    def calculate_pull_request_pairwise_conflicts(self, pull_requests):
        pairwise_conflict_by_pull_request = {}
        for pull_request in pull_requests:
            pairwise_conflict_pull_requests = []
            prs = self.ghtorrent_db.get_pull_requests_between(pull_request.opened_at, pull_request.closed_at)
            for pr in prs:
                if self.conflicting_pull_requests(pull_request, pr) > 0:
                    pairwise_conflict_pull_requests.append(pr)
            pairwise_conflict_by_pull_request[str(pull_request.pullreq_id)] = [str(p.pullreq_id) for p in pairwise_conflict_pull_requests]
        return pairwise_conflict_by_pull_request

    def conflicting_pull_requests(self, a_pull_request, another_pull_request):
        # Buscar las versiones a mergear de cada pull requests
        # luego tratar de mergearlas
        ret = 0
        if a_pull_request.base_branch != another_pull_request.base_branch:
            return ret

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
        if a_pull_request_commit and another_pull_request_commit:
            commit_sha_1 = a_pull_request_commit.sha
            commit_sha_2 = another_pull_request_commit.sha

            print("Merge de commit {} en el commit {}".format(commit_sha_2, commit_sha_1))

            ret = int(self.git.conflicting_merge(commit_sha_1, commit_sha_2))

        return ret


class PairwiseConflictGraphAnalyzer(object):

    def __init__(self, project_name, pull_requests):
        self.project_name = project_name
        pairwise_conflict_analyzer = PairwiseConflictAnalyzer(project_name=project_name)
        self.pairwise_conflict_by_pull_request = pairwise_conflict_analyzer.get_pairwise_conflict_by_pull_request()
        self.pull_request_ids = [str(pr.pullreq_id) for pr in pull_requests]
        self.conflict_matrix_path = settings.CONFLICT_MATRIX_PATH
        self.graph = self.make_graph(pull_requests)
    
    def make_graph(self, pull_requests):
        graph = []
        # Row
        for a_pull_request in pull_requests:
            a_pull_request_pairwise_conflict = self.pairwise_conflict_by_pull_request.get(str(a_pull_request.pullreq_id), [])
            new_row = []
            # Column
            for another_pull_request in pull_requests:
                if str(another_pull_request.pullreq_id) in a_pull_request_pairwise_conflict:
                    value = 1 
                else:
                    value = 0
                new_row.append(value)
            graph.append(new_row)
        print(graph)
        return graph
                
    def get_groups_weight(self):
        self.save_graph()
        groups = []
        result = subprocess.run(['java','-jar', 'matrix.jar'],
                                cwd=self.conflict_matrix_path, capture_output=True)

        groups_str = result.stdout.decode('utf-8').split('\n')[:-1]
        for group_str in groups_str:
            groups.append(group_str.split(','))

        return [len(group) for group in groups]

    def save_graph(self):
        filename = '{}/matrix.csv'.format(self.conflict_matrix_path)
        with open(filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['0'] + self.pull_request_ids)
            for i in range(len(self.pull_request_ids)):
                csv_writer.writerow([self.pull_request_ids[i]] + self.graph[i])
