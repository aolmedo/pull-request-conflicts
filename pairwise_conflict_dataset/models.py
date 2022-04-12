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
    default_branch = models.CharField(_(u'default branch'), max_length=255, null=True, blank=True)
    # first_pc_date = models.DateTimeField(_(u'first pairwise conflict date'), null=True, blank=True)
    # last_pc_date = models.DateTimeField(_(u'last pairwise conflict date'), null=True, blank=True)
    pairwise_conflicts_count = models.PositiveIntegerField(_(u'pairwise conflict count'), null=True, blank=True)
    data_quality_percentage = models.DecimalField(_(u'data quality (%)'), max_digits=10, decimal_places=2,
                                                  null=True, blank=True)
    raw_data = models.JSONField(_(u'raw data'))
    github_raw_data = models.JSONField(_(u'github raw data'), null=True, blank=True)

    def get_pairwise_conflicts_count(self, recalculate=False):
        if recalculate:
            pairwise_conflicts_count = 0
            for pull_request in self.pull_requests.all():
                pairwise_conflicts_count += pull_request.first_pairwise_conflicts.count() + \
                                            pull_request.second_pairwise_conflicts.count()
            self.pairwise_conflicts_count = int(pairwise_conflicts_count / 2)
            self.save()
        return self.pairwise_conflicts_count

    def get_data_quality_percentage(self, recalculate=False):
        if recalculate:
            ok_count = 0
            for pull_request in self.pull_requests.filter(merged=True):
                if pull_request.head_commit and \
                        str(pull_request.project.ghtorrent_id) == pull_request.head_commit.raw_data.get('project_id'):
                    ok_count += 1
            self.data_quality_percentage = (ok_count / self.pull_requests.count()) * 100
            self.save()
        return self.data_quality_percentage

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("project")
        verbose_name_plural = _("projects")


class Commit(models.Model):
    ghtorrent_id = models.PositiveIntegerField(_(u'GHTorrent ID'))
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name="project", related_name='commits')
    sha = models.CharField(_(u'sha'), max_length=40)
    created_at = models.DateTimeField(_(u'created at'))
    raw_data = models.JSONField(_(u'raw data'))

    def __str__(self):
        return self.sha

    class Meta:
        ordering = ["created_at"]
        verbose_name = _("commit")
        verbose_name_plural = _("commits")


class PullRequest(models.Model):
    ghtorrent_id = models.PositiveIntegerField(_(u'GHTorrent ID'))
    project = models.ForeignKey(Project, on_delete=models.PROTECT,
                                verbose_name="project", related_name='pull_requests')
    github_id = models.PositiveIntegerField(_(u'github id'))
    base_commit = models.ForeignKey(Commit, on_delete=models.PROTECT, null=True, blank=True,
                                    verbose_name="base commit", related_name='base_pull_requests')
    head_commit = models.ForeignKey(Commit, on_delete=models.PROTECT, null=True, blank=True,
                                    verbose_name="head commit", related_name='head_pull_requests')
    intra_branch = models.BooleanField(_(u'is intra branch?'))
    merged = models.BooleanField(_(u'is merged?'))
    opened_at = models.DateTimeField(_(u'opened at'))
    closed_at = models.DateTimeField(_(u'closed at'), null=True, blank=True)
    base_branch = models.CharField(_(u'target branch'), max_length=255, null=True, blank=True)
    raw_data = models.JSONField(_(u'raw data'))
    github_raw_data = models.JSONField(_(u'github raw data'), null=True, blank=True)

    def __str__(self):
        return "#{}".format(self.github_id)

    class Meta:
        ordering = ["opened_at"]
        verbose_name = _("pull request")
        verbose_name_plural = _(u"pull requests")


class PairwiseConflict(models.Model):
    first_pull_request = models.ForeignKey(PullRequest, on_delete=models.PROTECT, verbose_name="first pull request",
                                           related_name='first_pairwise_conflicts')
    second_pull_request = models.ForeignKey(PullRequest, on_delete=models.PROTECT, verbose_name="second pull request",
                                            related_name='second_pairwise_conflicts')

    def __str__(self):
        return "Pairwise conflict between: {} and {}".format(self.first_pull_request, self.second_pull_request)

    class Meta:
        ordering = ["id"]
        verbose_name = _("pairwise conflict")
        verbose_name_plural = _(u"pairwise conflicts")
