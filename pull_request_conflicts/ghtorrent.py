# -*- coding: utf-8 -*-
import psycopg2
import settings
from models import PullRequest, Commit


class GHTorrentDB(object):
    """
        ghtorrent database
    """

    def __init__(self, pull_request_table_name):
        dsn = "dbname={} user={} host={} port={}".format(settings.DB_NAME,
            settings.DB_USER, settings.DB_HOST, settings.DB_PORT)
        self.conn = psycopg2.connect(dsn)
        self.pull_request_table_name = pull_request_table_name

    def get_pull_requests(self):
        pull_requests = []
        query = "SELECT id, head_repo_id, base_repo_id, head_commit_id, base_commit_id, " \
                "pullreq_id, intra_branch, merged, opened_at, closed_at FROM {} " \
                "ORDER BY opened_at".format(self.pull_request_table_name)
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, {})
                for pr_data in cursor.fetchall():
                    pr = PullRequest(*pr_data)
                    pull_requests.append(pr)
        return pull_requests

    def get_merged_pull_requests(self):
        pull_requests = []
        query = "SELECT id, head_repo_id, base_repo_id, head_commit_id, base_commit_id, " \
                "pullreq_id, intra_branch, merged, opened_at, closed_at FROM {} WHERE " \
                "merged = %(merged)s ORDER BY opened_at".format(self.pull_request_table_name)
        params = {'merged': True}
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                for pr_data in cursor.fetchall():
                    pr = PullRequest(*pr_data)
                    pull_requests.append(pr)
        return pull_requests

    def get_pull_requests_between(self, date_from, date_to):
        pull_requests = []
        query = "SELECT id, head_repo_id, base_repo_id, head_commit_id, base_commit_id, " \
                "pullreq_id, intra_branch, merged, opened_at, closed_at FROM {} WHERE " \
                "(opened_at < %(date_from)s AND closed_at > %(date_from)s) " \
                "OR (opened_at > %(date_from)s AND opened_at < %(date_to)s) " \
                "ORDER BY opened_at".format(self.pull_request_table_name)
        params = {'date_from': date_from, 'date_to': date_to}
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                for pr_data in cursor.fetchall():
                    pr = PullRequest(*pr_data)
                    pull_requests.append(pr)
        return pull_requests

    def get_commit_children(self, commit_id):
        commits = []
        query = "SELECT commit_id FROM commit_parents where parent_id = %(commit_id)s;"
        params = {'commit_id': commit_id}
        commit_query = 'SELECT * FROM commits WHERE id = %(commit_id)s'
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                commit_ids = cursor.fetchall()
                for commit_id in commit_ids:
                    cursor.execute(commit_query, {'commit_id': commit_id})
                    commit_data = cursor.fetchone()
                    commit = Commit(*commit_data)
                    commits.append(commit)
        return commits

    def get_commit_parents(self, commit_id):
        commits = []
        query = "SELECT parent_id FROM commit_parents where commit_id = %(commit_id)s;"
        params = {'commit_id': commit_id}
        commit_query = 'SELECT * FROM commits WHERE id = %(commit_id)s'
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                commit_ids = cursor.fetchall()
                for commit_id in commit_ids:
                    cursor.execute(commit_query, {'commit_id': commit_id})
                    commit_data = cursor.fetchone()
                    commit = Commit(*commit_data)
                    commits.append(commit)
        return commits

    def get_commit(self, commit_id):
        commit = None
        query = "SELECT * FROM commits WHERE id = %(commit_id)s"
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, {'commit_id': commit_id})
                commit_data = cursor.fetchone()
                commit = Commit(*commit_data)
        return commit

    def get_pull_requests_commits(self, pull_request):
        commits = []
        query = "SELECT * FROM commits WHERE id IN " \
            "(SELECT commit_id FROM pull_request_commits WHERE " \
                "pull_request_id = %(pull_request_id)s)"
        params = {'pull_request_id': pull_request.id}
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                commits_data = cursor.fetchall()
                for commit_data in commits_data:
                    commit = Commit(*commit_data)
                    commits.append(commit)
        return commits

    def set_pull_request_conflicting_merge(self, pull_request):
        query = "UPDATE {} SET conflicting_merge = 't' WHERE " \
            "id = %(id)s".format(self.pull_request_table_name)
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, {'id': pull_request.id})

    def set_pull_request_merge_conflict_amount(self, pull_request, merge_conflict_amount):
        query = "UPDATE {} SET merge_conflict_amount = %(merge_conflict_amount)s WHERE " \
            "id = %(id)s".format(self.pull_request_table_name)
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, {'id': pull_request.id,
                                       'merge_conflict_amount': merge_conflict_amount})
