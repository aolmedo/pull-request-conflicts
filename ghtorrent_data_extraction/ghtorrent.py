# -*- coding: utf-8 -*-
import psycopg2
from . import settings
from .models import Project


class GHTorrentDB(object):
    """
        ghtorrent database connector
    """

    def __init__(self):
        dsn = "dbname={} user={} host={} port={}".\
            format(settings.DB_NAME, settings.DB_USER, settings.DB_HOST, settings.DB_PORT)
        self.conn = psycopg2.connect(dsn)

    def execute(self, query, params={}):
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)

    def execute_query(self, query, params={}):
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()

    def copy_to(self, a_sql, a_file):
        with self.conn as conn:
            with conn.cursor() as cursor:
                cursor.copy_expert(a_sql, a_file)

    def get_selected_projects(self):
        projects = []
        query = "SELECT * FROM selected_projects WHERE id = %(id)s"
        ret = self.execute_query(query, {'id': 17302594})
        for data in ret:
            project = Project(*data)
            projects.append(project)
        return projects

    def extract_pull_requests_for_project(self, project):
        query = "CREATE TABLE {}_pull_requests AS (SELECT * FROM pull_requests WHERE base_repo_id = %(id)s)".\
                format(project.name.lower())
        self.execute(query, {'id': project.id})

    def extract_commits_for_project(self, project):
        query = "CREATE TABLE {}_commits AS (SELECT * FROM commits WHERE project_id = %(id)s "\
                "OR id IN (SELECT head_commit_id FROM {}_pull_requests))".\
                format(project.name.lower(), project.name.lower())
        self.execute(query, {'id': project.id})

    def export_selected_projects(self):
        query = "COPY (SELECT * FROM selected_projects ORDER BY created_at) TO STDOUT " \
                    "DELIMITER ',' CSV HEADER"
        file_path = settings.GHTORRENT_EXPORT_PATH + "/projects.csv"
        with open(file_path, "w") as table_file:
            self.copy_to(query, table_file)

    def export_pull_requests_for_project(self, project):
        query = "COPY (SELECT * FROM {}_pull_requests ORDER BY opened_at) TO STDOUT " \
                "DELIMITER ',' CSV HEADER".format(project.name.lower())
        file_path = settings.GHTORRENT_EXPORT_PATH + "/{}_pull_requests.csv".format(project.name.lower())
        with open(file_path, "w") as table_file:
            self.copy_to(query, table_file)

    def export_commits_for_project(self, project):
        query = "COPY (SELECT * FROM {}_commits ORDER BY created_at) TO STDOUT "\
                "DELIMITER ',' CSV HEADER".format(project.name.lower())
        file_path = settings.GHTORRENT_EXPORT_PATH + "/{}_commits.csv".format(project.name.lower())
        with open(file_path, "w") as table_file:
            self.copy_to(query, table_file)
