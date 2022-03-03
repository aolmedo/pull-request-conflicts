from django.contrib import admin
from django.urls import reverse
from django.utils.html import mark_safe
from ipe_analysis.models import IPETimeWindow


class IPETimeWindowAdmin(admin.ModelAdmin):
    list_display = ('project', 'start_date', 'end_date', 'pull_requests_number', 'pairwise_conflicts_number',
                    'potential_conflict_resolutions_number', 'unconflicting_pull_request_groups_number',
                    'historical_conflict_resolutions_number', 'historical_ipe', 'optimized_conflict_resolutions_number',
                    'optimized_ipe', 'ipe_improvement_percentage', 'view_detail')

    readonly_fields = ('project', 'start_date', 'end_date', 'pull_requests_number', 'pairwise_conflicts_number',
                       'potential_conflict_resolutions_number', 'unconflicting_pull_request_groups_number',
                       'historical_conflict_resolutions_number', 'historical_ipe',
                       'optimized_conflict_resolutions_number', 'optimized_ipe', 'ipe_improvement_percentage',
                       'pairwise_conflict_graph_image', 'colored_pairwise_conflict_graph_image',
                       'pull_request_group_graph_image', 'integration_trajectories_image')

    @admin.display()
    def view_detail(self, obj):
        return mark_safe('<a class="grp-button" href="{}" target="blank">{}</a>'.format(
            reverse('ipe-time-window-detail', kwargs={'pk': obj.id}), 'view'))

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(IPETimeWindow, IPETimeWindowAdmin)
