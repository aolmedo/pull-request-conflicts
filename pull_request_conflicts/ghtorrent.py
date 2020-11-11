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
        query = "SELECT * FROM {} WHERE intra_branch = %(intra_branch)s AND "\
            "merged = %(merged)s".format(self.pull_request_table_name)
        params = {'intra_branch': True, 'merged': True}
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

    def set_pull_request_conflicting_merge(self, pull_request):
        query = "UPDATE {} SET conflicting_merge = 't' WHERE " \
            "id = %(id)s".format(self.pull_request_table_name)
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, {'id': pull_request.id})
