# -*- coding: utf-8 -*-
import subprocess


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
    def __init__(self, repo_path, repo_head):
        self.repo_path = repo_path
        self.repo_head = repo_head

    def merge(self, commit_sha):
        """
            merge the commit @commit_sha into the current version.
        """
        result = subprocess.run(['git','merge', commit_sha, '--no-commit', '--no-ff'],
                                cwd=self.repo_path, capture_output=True)
        if result.returncode == 1:
            raise MergeConflictDetected()

    def merge_abort(self):
        """
            merge abort.
        """
        result = subprocess.run(['git','merge', '--abort'],
                                cwd=self.repo_path, capture_output=True)
        if result.returncode != 0:
            raise MergeAbortFail()

    def checkout(self, commit_sha):
        """
            checkout the commit @commit_sha
        """
        result = subprocess.run(['git','checkout', commit_sha],
                                cwd=self.repo_path, capture_output=True)
        if result.returncode != 0:
            raise VersionNotFound(result.stderr)

    def conflicting_merge(self, commit_sha_1, commit_sha_2):
        """
            merge commit @commit_sha_2 into commit @commit_sha_1
        """
        merge_conflict = False
        try:
            self.checkout(commit_sha_1)
        except VersionNotFound:
            print("No se encontro la version {}".format(commit_sha_1))
            self.checkout(self.repo_head)
            return False
        try:
            self.merge(commit_sha_2)
        except MergeConflictDetected:
            merge_conflict = True
        try:
            self.merge_abort()
        except MergeAbortFail:
            print("Ocurrio un problema al querer abortar el merge entre la version {} y la version {}".format(commit_sha_1, commit_sha_2))
        self.checkout(self.repo_head)
        return merge_conflict
