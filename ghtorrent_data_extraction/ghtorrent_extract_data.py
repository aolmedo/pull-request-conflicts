# -*- coding: utf-8 -*-
from ghtorrent import GHTorrentDB


if __name__ == "__main__":

    projects = GHTorrentDB.get_selected_projects()

    for project in projects:
        GHTorrentDB.extract_pull_requests_for_project(project)
        GHTorrentDB.export_pull_requests_for_project(project)
        GHTorrentDB.extract_commits_for_project(project)
        GHTorrentDB.export_commits_for_project(project)

