import json
from django.contrib import admin
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.html import mark_safe
from import_export import resources
from import_export.admin import ExportMixin
from pairwise_conflict_dataset.models import Project, Commit, PullRequest, PairwiseConflict


class ProjectResource(resources.ModelResource):

    class Meta:
        model = Project
        fields = ('name', 'description', 'github_url', 'language', 'created_at')
        export_order = ('name', 'description', 'github_url', 'language', 'created_at')


class ProjectAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('name', 'description', 'github_url_link', 'language', 'created_at', 'pull_requests_count',
                    'commits_count', 'pairwise_conflicts_count')
    date_hierarchy = 'created_at'
    list_filter = ('language',)
    search_fields = ['name',]
    readonly_fields = ('ghtorrent_id', 'name', 'description', 'github_url', 'api_url', 'language', 'created_at',
                       'default_branch', 'pairwise_conflicts_count', 'data_quality_percentage', 'raw_data',
                       'github_raw_data')
    resource_class = ProjectResource

    @admin.display()
    def github_url_link(self, obj):
        return mark_safe('<a class="grp-button" href="{}" target="blank">{}</a>'.format(obj.github_url, obj.github_url))

    @admin.display(ordering='pull_requests__count')
    def pull_requests_count(self, obj):
        return obj.pull_requests.count()

    @admin.display(ordering='commits__count')
    def commits_count(self, obj):
        return obj.commits.count()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class CommitResource(resources.ModelResource):

    class Meta:
        model = Commit
        fields = ('project', 'sha', 'created_at')
        export_order = ('project', 'sha', 'created_at')


class CommitAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('project', 'sha', 'created_at')
    date_hierarchy = 'created_at'
    list_filter = ('project',)
    search_fields = ['project__name', ]
    readonly_fields = ('ghtorrent_id', 'project', 'sha', 'created_at', 'raw_data')
    resource_class = CommitResource

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('github_id', 'project', 'intra_branch', 'merged', 'opened_at', 'closed_at', 'head_commit_link',
                    'base_branch', 'pairwise_conflicts_count')
    date_hierarchy = 'closed_at'
    list_filter = ('intra_branch', 'merged', 'project')
    search_fields = ['github_id', 'project__name', 'base_branch']
    readonly_fields = ('ghtorrent_id', 'project', 'github_id', 'base_commit', 'head_commit', 'intra_branch', 'merged',
                       'opened_at', 'closed_at', 'base_branch', 'raw_data', 'github_raw_data')

    @admin.display(description='head_commit')
    def head_commit_link(self, obj):
        return mark_safe(
            '<a class="grp-button" href="{}/commit/{}" target="blank">{}</a>'.format(
                obj.project.github_url,
                obj.head_commit,
                obj.head_commit))

    @admin.display()
    def pairwise_conflicts_count(self, obj):
        return obj.first_pairwise_conflicts.count() + obj.second_pairwise_conflicts.count()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        cl = self.get_changelist_instance(request)
        result_list = [pc.id for pc in cl.queryset.all()]
        # Aggregate new subscribers per day
        chart_data = (
            PullRequest.objects.filter(merged=True, id__in=result_list).annotate(date=TruncDay("closed_at"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)


class PairwiseConflictAdmin(admin.ModelAdmin):
    list_display = ('project', 'first_pull_request', 'second_pull_request', 'first_pull_request_head_commit',
                    'second_pull_request_head_commit', 'first_pull_request_base_branch',
                    'first_pull_request_closed_at', 'second_pull_request_closed_at')
    date_hierarchy = 'first_pull_request__closed_at'
    readonly_fields = ('first_pull_request', 'second_pull_request',)
    search_fields = ['first_pull_request__github_id', 'second_pull_request__github_id',
                     'first_pull_request__project__name', 'first_pull_request__base_branch']

    @admin.display(ordering='first_pull_request__project__name')
    def project(self, obj):
        return obj.first_pull_request.project

    @admin.display(ordering='first_pull_request__head_commmit__created_at')
    def first_pull_request_head_commit(self, obj):
            return mark_safe(
                '<a class="grp-button" href="{}/commit/{}" target="blank">{}</a>'.format(
                    obj.first_pull_request.project.github_url,
                    obj.first_pull_request.head_commit,
                    obj.first_pull_request.head_commit))

    @admin.display(ordering='second_pull_request__head_commmit__created_at')
    def second_pull_request_head_commit(self, obj):
        return mark_safe(
            '<a class="grp-button" href="{}/commit/{}" target="blank">{}</a>'.format(
                obj.second_pull_request.project.github_url,
                obj.second_pull_request.head_commit,
                obj.second_pull_request.head_commit))

    @admin.display(ordering='second_pull_request__base_branch')
    def first_pull_request_base_branch(self, obj):
        return obj.second_pull_request.base_branch

    @admin.display(ordering='first_pull_request__closed_at')
    def first_pull_request_closed_at(self, obj):
        return obj.first_pull_request.closed_at

    @admin.display(ordering='second_pull_request__closed_at')
    def second_pull_request_closed_at(self, obj):
        return obj.second_pull_request.closed_at

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        cl = self.get_changelist_instance(request)
        result_list = [pc.id for pc in cl.queryset.all()]
        # Aggregate new subscribers per day
        chart_data = (
            PairwiseConflict.objects.filter(id__in=result_list).annotate(date=TruncDay("first_pull_request__closed_at"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        as_json = json.dumps(list(chart_data), cls=DjangoJSONEncoder)
        extra_context = extra_context or {"chart_data": as_json}

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)


admin.site.register(Project, ProjectAdmin)
admin.site.register(Commit, CommitAdmin)
admin.site.register(PullRequest, PullRequestAdmin)
admin.site.register(PairwiseConflict, PairwiseConflictAdmin)
