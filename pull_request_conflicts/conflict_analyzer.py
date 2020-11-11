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
            head_commit = ghtorrent_db.get_commit(pull_request.head_commit_id)
            # Busco las versiones hijas de la version head (en principio deberia ser el merge contra master)
            commit_children = ghtorrent_db.get_commit_children(head_commit.id)
            # Para cada uno de los hijos, busco sus padres. En el caso de que tenga más de un padre es un merge.
            for commit in commit_children:
                commit_parents = ghtorrent_db.get_commit_parents(commit.id)
                # Saco el head_commit entre los padres del commit asi veo contra que mergear si es que hay mas de uno.
                commit_parents.remove(head_commit)
                # Si queda algún padre es por que se mergeo este con el otro. Entonces tengo que ver si hay conflictos.
                # Sino no hace nada.
                if commit_parents:
                    # Ver si hay conflictos
                    commit_into = commit_parents[0]
                    if git.conflicting_merge(commit_into.sha, head_commit.sha):
                        # El merge del PR tuvo conflictos que el usuario tuvo que resolver
                        # Marcarlo en la base de datos
                        ghtorrent_db.set_pull_request_conflicting_merge(pull_request)
