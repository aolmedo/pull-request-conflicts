# -*- coding: utf-8 -*-
import os
import re
import subprocess
from pairwise_conflict_dataset import settings


class CloneFail(Exception):
    pass


class VersionNotFound(Exception):
    pass


class MergeConflictDetected(Exception):
    pass


class MergeAbortFail(Exception):
    pass


class GitCommandLineInterface(object):
    """
        Git Command Line Interface
    """
    def __init__(self, project):
        self.repo_url = project.github_url
        self.repo_path = settings.REPOSITORIES_BASE_PATH + "/{}".format(project.name)
        self.repo_head = project.default_branch

    def clone(self):
        """
            clone github repository
        """
        if os.path.isdir(self.repo_path):
            return

        result = subprocess.run(['git', 'clone', self.repo_url],
                                cwd=settings.REPOSITORIES_BASE_PATH, capture_output=True)
        if result.returncode != 0:
            raise CloneFail()

    def merge(self, commit_sha):
        """
            merge the commit @commit_sha into the current version.
        """
        result = subprocess.run(['git', 'merge', commit_sha, '--no-commit', '--no-ff'],
                                cwd=self.repo_path, capture_output=True)

        stdout = result.stdout
        stdout = stdout.decode('utf-8')
        lines = stdout.split('\n')
        if len(lines) >= 2:
            regex = r'.*Fusión automática falló; arregle los conflictos y luego realice un commit con el resultado.*'
            result_text = lines[-2]
            if re.match(regex, result_text):
                raise MergeConflictDetected()

    def merge_abort(self):
        """
            merge abort.
        """
        result = subprocess.run(['git', 'merge', '--abort'],
                                cwd=self.repo_path, capture_output=True)
        if result.returncode != 0:
            raise MergeAbortFail()

    def checkout(self, commit_sha):
        """
            checkout the commit @commit_sha
        """
        result = subprocess.run(['git', 'checkout', commit_sha, '--force'],
                                cwd=self.repo_path, capture_output=True)
        if result.returncode != 0:
            raise VersionNotFound(result.stderr)

    def conflicting_merge(self, commit_sha_1, commit_sha_2):
        """
            merge commit @commit_sha_2 into commit @commit_sha_1
        """
        merge_conflict = 0
        try:
            self.checkout(commit_sha_1)
        except VersionNotFound:
            print("No se encontro la version {}".format(commit_sha_1))
            self.checkout(self.repo_head)
            return -1
        try:
            self.merge(commit_sha_2)
        except MergeConflictDetected:
            merge_conflict = 1
        try:
            self.merge_abort()
        except MergeAbortFail:
            pass
            # print("Ocurrio un problema al querer abortar el merge entre la version {} y la version {}"
            #      .format(commit_sha_1, commit_sha_2))
        self.checkout(self.repo_head)
        return merge_conflict
