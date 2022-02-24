# -*- coding: utf-8 -*-


class Project(object):

    def __init__(self, idx, url, owner_id, name, description, language, created_at, forked_from, deleted, updated_at,
                 forked_commit_id, *args, **kwargs):
        self.id = idx
        self.url = url
        self.owner_id = owner_id
        self.name = name
        self.description = description
        self.language = language
        self.created_at = created_at
        self.forked_from = forked_from
        self.deleted = deleted
        self.updated_at = updated_at
        self.forked_commit_id = forked_commit_id

    def __eq__(self, a_project):
        return self.id == a_project.id


class PullRequest(object):

    def __init__(self, idx, head_repo_id, base_repo_id, head_commit_id, base_commit_id,
                 pullreq_id, intra_branch, merged, opened_at, closed_at, base_branch, *args, **kwargs):
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
        self.base_branch = base_branch

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
