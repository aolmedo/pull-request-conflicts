# -*- coding: utf-8 -*-
from ghtorrent import GHTorrentDB


if __name__ == "__main__":

    ghtorrent_db = GHTorrentDB()
    projects = ghtorrent_db.get_selected_projects()
    total_count = len(projects)

    for i, project in enumerate(projects):
        print(i+1, "/", total_count)
        ghtorrent_db.extract_pull_requests_for_project(project)
        ghtorrent_db.export_pull_requests_for_project(project)
        ghtorrent_db.extract_commits_for_project(project)
        ghtorrent_db.export_commits_for_project(project)

