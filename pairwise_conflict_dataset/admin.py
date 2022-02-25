from django.contrib import admin
from django.utils.html import mark_safe
from pairwise_conflict_dataset.models import Project, Commit, PullRequest, PairwiseConflict


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'github_url_link', 'language', 'created_at', 'pull_requests_count',
                    'commits_count')
    date_hierarchy = 'created_at'
    list_filter = ('language',)
    search_fields = ['name',]
    readonly_fields = ('ghtorrent_id', 'name', 'description', 'github_url', 'api_url', 'language', 'created_at',
                       'default_branch', 'raw_data', 'github_raw_data')

    @admin.display()
    def github_url_link(self, obj):
        return mark_safe('<a class="grp-button" href="{}" target="blank">{}</a>'.format(obj.github_url, obj.github_url))

    @admin.display(ordering='pull_requests__count')
    def pull_requests_count(self, obj):
        return obj.pull_requests.count()

    @admin.display(ordering='commits__count')
    def commits_count(self, obj):
        return obj.commits.count()


class CommitAdmin(admin.ModelAdmin):
    list_display = ('project', 'sha', 'created_at')
    date_hierarchy = 'created_at'
    list_filter = ('project',)
    search_fields = ['project__name', ]
    readonly_fields = ('ghtorrent_id', 'project', 'sha', 'created_at', 'raw_data')


class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('github_id', 'project', 'intra_branch', 'merged', 'opened_at', 'closed_at', 'base_branch',
                    'pairwise_conflicts_count')
    date_hierarchy = 'closed_at'
    list_filter = ('intra_branch', 'merged', 'project')
    search_fields = ['github_id', 'project__name', 'base_branch']
    readonly_fields = ('ghtorrent_id', 'project', 'github_id', 'base_commit', 'head_commit', 'intra_branch', 'merged',
                       'opened_at', 'closed_at', 'base_branch', 'raw_data', 'github_raw_data')

    @admin.display(ordering='first_pairwise_conflicts__count')
    def pairwise_conflicts_count(self, obj):
        return obj.first_pairwise_conflicts.count() + obj.second_pairwise_conflicts.count()


class PairwiseConflictAdmin(admin.ModelAdmin):
    list_display = ('project', 'first_pull_request', 'second_pull_request', 'first_pull_request_head_commit',
                    'second_pull_request_head_commit', 'first_pull_request_base_branch')
    readonly_fields = ('first_pull_request', 'second_pull_request',)
    search_fields = ['first_pull_request__github_id', 'second_pull_request__github_id',
                     'first_pull_request__project__name', 'first_pull_request__base_branch']

    @admin.display(ordering='first_pull_request__project__name')
    def project(self, obj):
        return obj.first_pull_request.project

    @admin.display(ordering='first_pull_request__head_commmit__created_at')
    def first_pull_request_head_commit(self, obj):
        return obj.first_pull_request.head_commit

    @admin.display(ordering='second_pull_request__head_commmit__created_at')
    def second_pull_request_head_commit(self, obj):
        return obj.second_pull_request.head_commit

    @admin.display(ordering='second_pull_request__base_branch')
    def first_pull_request_base_branch(self, obj):
        return obj.second_pull_request.base_branch


admin.site.register(Project, ProjectAdmin)
admin.site.register(Commit, CommitAdmin)
admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(PairwiseConflict, PairwiseConflictAdmin)
