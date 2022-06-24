from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe
from import_export import resources
from import_export.admin import ExportMixin
from ipe_analysis.models import IPETimeWindow, ProjectIPEStats


class IPETimeWindowResource(resources.ModelResource):

    class Meta:
        model = IPETimeWindow
        fields = ('project__name', 'start_date', 'end_date', 'pull_requests_number', 'pairwise_conflicts_number',
                  'potential_conflict_resolutions_number', 'unconflicting_pull_request_groups_number',
                  'historical_conflict_resolutions_number', 'historical_ipe', 'optimized_conflict_resolutions_number',
                  'optimized_ipe', 'cr_improvement_percentage', 'ipe_improvement_percentage')
        export_order = ('project__name', 'start_date', 'end_date', 'pull_requests_number', 'pairwise_conflicts_number',
                        'potential_conflict_resolutions_number', 'unconflicting_pull_request_groups_number',
                        'historical_conflict_resolutions_number', 'historical_ipe',
                        'optimized_conflict_resolutions_number', 'optimized_ipe', 'cr_improvement_percentage',
                        'ipe_improvement_percentage')


class IPETimeWindowAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('project', 'tw_size', 'start_date', 'end_date', 'pull_requests_number', 'pairwise_conflicts_number',
                    'potential_conflict_resolutions_number', 'unconflicting_pull_request_groups_number',
                    'historical_conflict_resolutions_number', 'historical_ipe', 'optimized_conflict_resolutions_number',
                    'optimized_ipe', 'cr_improvement_percentage', 'ipe_improvement_percentage', 'view_detail')
    date_hierarchy = 'start_date'
    list_filter = ('project', 'tw_size',)
    search_fields = ['project__name', ]
    readonly_fields = ('project', 'tw_size', 'start_date', 'end_date', 'pull_requests_number', 'pairwise_conflicts_number',
                       'potential_conflict_resolutions_number', 'unconflicting_pull_request_groups_number',
                       'historical_conflict_resolutions_number', 'historical_ipe',
                       'optimized_conflict_resolutions_number', 'optimized_ipe', 'cr_improvement_percentage',
                       'ipe_improvement_percentage', 'pairwise_conflict_graph_image',
                       'colored_pairwise_conflict_graph_image', 'pull_request_group_graph_image',
                       'integration_trajectories_image')
    resource_class = IPETimeWindowResource

    @admin.display()
    def view_detail(self, obj):
        return mark_safe('<a class="grp-button" href="{}" target="blank">{}</a>'.format(
            reverse('ipe-time-window-detail', kwargs={'pk': obj.id}), 'view'))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class ProjectIPEStatsResource(resources.ModelResource):

    class Meta:
        model = ProjectIPEStats
        fields = ('project__name', 'tw_size', 'tw_quantity', 'tw_with_pc_percentage', 'tw_improves_cr_quantity',
                  'tw_equal_cr_quantity', 'tw_improves_ipe_quantity', 'tw_equal_ipe_quantity',
                  'tw_worsen_ipe_quantity', 'cr_improvement_percentage_min', 'cr_improvement_percentage_mean',
                  'cr_improvement_percentage_std', 'cr_improvement_percentage_max', 'ipe_improvement_percentage_min',
                  'ipe_improvement_percentage_mean', 'ipe_improvement_percentage_std', 'ipe_improvement_percentage_max')

        export_order = ('project__name', 'tw_size', 'tw_quantity', 'tw_with_pc_percentage', 'tw_improves_cr_quantity',
                        'tw_equal_cr_quantity', 'tw_improves_ipe_quantity', 'tw_equal_ipe_quantity',
                        'tw_worsen_ipe_quantity', 'cr_improvement_percentage_min', 'cr_improvement_percentage_mean',
                        'cr_improvement_percentage_std', 'cr_improvement_percentage_max',
                        'ipe_improvement_percentage_min', 'ipe_improvement_percentage_mean',
                        'ipe_improvement_percentage_std', 'ipe_improvement_percentage_max')


class ProjectIPEStatsAdmin(ExportMixin, admin.ModelAdmin):
    list_display = ('project', 'tw_size', 'tw_quantity', 'tw_with_pc_percentage', 'tw_improves_cr_quantity',
                    'tw_equal_cr_quantity', 'tw_improves_ipe_quantity', 'tw_equal_ipe_quantity',
                    'tw_worsen_ipe_quantity', 'cr_improvement_percentage_min', 'cr_improvement_percentage_mean',
                    'cr_improvement_percentage_std', 'cr_improvement_percentage_max', 'ipe_improvement_percentage_min',
                    'ipe_improvement_percentage_mean', 'ipe_improvement_percentage_std',
                    'ipe_improvement_percentage_max')
    list_filter = ('project', 'tw_size',)
    search_fields = ['project__name', ]
    readonly_fields = ('project', 'tw_size', 'tw_quantity', 'tw_with_pc_percentage', 'tw_improves_cr_quantity',
                       'tw_equal_cr_quantity', 'tw_improves_ipe_quantity', 'tw_equal_ipe_quantity',
                       'tw_worsen_ipe_quantity', 'cr_improvement_percentage_min', 'cr_improvement_percentage_mean',
                       'cr_improvement_percentage_std', 'cr_improvement_percentage_max',
                       'ipe_improvement_percentage_min', 'ipe_improvement_percentage_mean',
                       'ipe_improvement_percentage_std', 'ipe_improvement_percentage_max')
    resource_class = ProjectIPEStatsResource

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(IPETimeWindow, IPETimeWindowAdmin)
admin.site.register(ProjectIPEStats, ProjectIPEStatsAdmin)
