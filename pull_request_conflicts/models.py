# -*- coding: utf-8 -*-


class PullRequest(object):

    def __init__(self, idx, head_repo_id, base_repo_id, head_commit_id, base_commit_id,
                 pullreq_id, intra_branch, merged, opened_at, closed_at, *args, **kwargs):
        self.id = idx
        self.head_repo_id = head_repo_id
        self.base_repo_id = base_repo_id
        self.head_commit_id = head_commit_id
        self.base_commit_id = base_commit_id
        self.pullreq_id = pullreq_id
        self.intra_branch = intra_branch
        self.merged = merged
        self.opened_at = opened_at
        self.closed_at = closed_at

    def __eq__(self, a_pull_request):
        return self.id == a_pull_request.id


class Commit(object):

    def __init__(self, idx, sha, author_id, committer_id, project_id, created_at, *args, **kwargs):
        self.id = idx
        self.sha = sha
        self.author_id = author_id
        self.committer_id = committer_id
        self.project_id = project_id
        self.created_at = created_at

    def __eq__(self, a_commit):
        return self.id == a_commit.id
