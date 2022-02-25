from django.contrib import admin
from pairwise_conflict_dataset.models import Project, Commit, PullRequest, PairwiseConflict


class ProjectAdmin(admin.ModelAdmin):
    pass


class CommitAdmin(admin.ModelAdmin):
    pass


class PullRequestAdmin(admin.ModelAdmin):
    pass


class PairwiseConflictAdmin(admin.ModelAdmin):
    pass


admin.site.register(Project, ProjectAdmin)
admin.site.register(Commit, CommitAdmin)
admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(PairwiseConflict, PairwiseConflictAdmin)
