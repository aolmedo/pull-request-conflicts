from django.db import models
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    ghtorrent_id = models.PositiveIntegerField(_(u'GHTorrent ID'))
    name = models.CharField(_(u'name'), max_length=255)
    description = models.TextField(_(u'description'))
    github_url = models.URLField(_(u'github url'))
    api_url = models.URLField(_(u'github api url'))
    language = models.CharField(_(u'language'), max_length=255)
    created_at = models.DateTimeField(_(u'created at'))
    raw_data = models.JSONField(_(u'raw data'))

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    # self.id = idx -> ok
    # self.url = url -> repo_url and api_url
    # self.owner_id = owner_id -> raw_data
    # self.name = name -> ok
    # self.description = description -> ok
    # self.language = language -> ok
    # self.created_at = created_at -> ok
    # self.forked_from = forked_from -> raw_data
    # self.deleted = deleted -> raw_data
    # self.updated_at = updated_at -> raw_data
    # self.forked_commit_id = forked_commit_id -> raw_data


class Commit(models.Model):
    ghtorrent_id = models.PositiveIntegerField(_(u'GHTorrent ID'))
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name="project", related_name='commits')
    sha = models.CharField(_(u'sha'), max_length=40)
    created_at = models.DateTimeField(_(u'created at'))

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("commit")
        verbose_name_plural = _("commits")

    # self.id = idx -> ok
    # self.sha = sha -> ok
    # self.author_id = author_id -> raw_data
    # self.committer_id = committer_id -> raw_data
    # self.project_id = project_id -> Foreing Key to Project
    # self.created_at = created_at -> ok


class PullRequest(models.Model):
    ghtorrent_id = models.PositiveIntegerField(_(u'GHTorrent ID'))
    project = models.ForeignKey(Project, on_delete=models.PROTECT,
                                verbose_name="project", related_name='pull_requests')
    github_id = models.PositiveIntegerField(_(u'github id'))
    base_commit = models.ForeignKey(Commit, on_delete=models.PROTECT,
                                    verbose_name="base commit", related_name='base_pull_requests')
    head_commit = models.ForeignKey(Commit, on_delete=models.PROTECT, null=True, blank=True,
                                    verbose_name="head commit", related_name='head_pull_requests')
    intra_branch = models.BooleanField(_(u'is intra branch?'))
    merged = models.BooleanField(_(u'is merged?'))
    opened_at = models.DateTimeField(_(u'opened at'))
    closed_at = models.DateTimeField(_(u'closed at'))
    base_branch = models.CharField(_(u'target branch'), max_length=255, null=True, blank=True)
    raw_data = models.JSONField(_(u'raw data'))

    class Meta:
        ordering = ["opened_at"]
        verbose_name = _("pull request")
        verbose_name_plural = _(u"pull requests")

    # self.id = idx -> ok
    # self.head_repo_id = head_repo_id -> raw_data
    # self.base_repo_id = base_repo_id -> Foreing Key to Project
    # self.head_commit_id = head_commit_id -> Foreign Key to Commit. Null. Blank.
    # self.base_commit_id = base_commit_id -> Foreign Key to Commit. not null.
    # self.pullreq_id = pullreq_id - > ok
    # self.intra_branch = intra_branch -> ok
    # self.merged = merged -> ok
    # self.opened_at = opened_at -> ok
    # self.closed_at = closed_at -> ok

    # no viene de ghtorrent
    # self.base_branch = base_branch -> ok. null. blank


class PairwiseConflict(models.Model):
    first_pull_request = models.ForeignKey(PullRequest, on_delete=models.PROTECT, verbose_name="first pull request",
                                           related_name='first_pairwise_conflicts')
    second_pull_request = models.ForeignKey(PullRequest, on_delete=models.PROTECT, verbose_name="second pull request",
                                            related_name='second_pairwise_conflicts')

    class Meta:
        ordering = ["id"]
        verbose_name = _("pairwise conflict")
        verbose_name_plural = _(u"pairwise conflicts")
