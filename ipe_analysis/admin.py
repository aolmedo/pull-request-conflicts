from django.contrib import admin
from ipe_analysis.models import IPETimeWindow


class IPETimeWindowAdmin(admin.ModelAdmin):
    list_display = ('project', 'start_date', 'end_date', 'pull_requests_number', 'pairwise_conflicts_number',
                    'potential_conflict_resolutions_number', 'unconflicting_pull_request_groups_number',
                    'historical_conflict_resolutions_number', 'historical_ipe', 'optimized_conflict_resolutions_number',
                    'optimized_ipe', 'ipe_improvement_percentage')


admin.site.register(IPETimeWindow, IPETimeWindowAdmin)
