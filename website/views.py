from django.shortcuts import render
import json
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.core.serializers.json import DjangoJSONEncoder
from django.views.generic import TemplateView, DetailView
from pairwise_conflict_dataset.models import Project, PairwiseConflict
from ipe_analysis.models import IPETimeWindow, IPECalculation


class HomeView(TemplateView):
    template_name = "index.html"


class IPETimeWindowDetailView(DetailView):
    model = IPETimeWindow

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ipe_data = IPECalculation(self.object.project, self.object.start_date, self.object.end_date)
        pull_request_ids = ipe_data.pcga.pull_request_ids
        groups_ids = ipe_data.pcga.optimal_integration_sequence
        historical_cost_gain_function = ipe_data.historical_cost_gain_function()
        optimized_cost_gain_function = ipe_data.optimized_cost_gain_function()
        historical_integration_sequence = [(i+1, pull_request_ids[i], historical_cost_gain_function[i][0],
                                            historical_cost_gain_function[i][1])
                                           for i in range(len(historical_cost_gain_function))]
        optimized_integration_sequence = [(i+1, groups_ids[i], optimized_cost_gain_function[i][0],
                                           optimized_cost_gain_function[i][1])
                                          for i in range(len(groups_ids))]
        context['historical_integration_sequence'] = historical_integration_sequence
        context['optimized_integration_sequence'] = optimized_integration_sequence
        return context


class ProjectIPEStatsDetailView(DetailView):
    model = Project

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # PRs info
        prs_number = self.object.pull_requests.count()
        merged_prs_number = self.object.pull_requests.filter(merged=True).count()
        intra_branch_merged_prs_number = self.object.pull_requests.filter(merged=True, intra_branch=True).count()
        first_pr_date = self.object.pull_requests.order_by('opened_at').first().opened_at
        last_pr_date = self.object.pull_requests.order_by('opened_at').last().opened_at

        pr_chart_data = (
            self.object.pull_requests.filter(merged=True).annotate(date=TruncDay("closed_at"))
            .values("date")
            .annotate(y=Count("id"))
            .order_by("-date")
        )
        # Serialize and attach the chart data to the template context
        pr_chart_data = json.dumps(list(pr_chart_data), cls=DjangoJSONEncoder)

        # Pairwise conflicts info
        pc_number = self.object.pairwise_conflicts_count
        first_pc_date = PairwiseConflict.objects.filter(first_pull_request__project=self.object)\
            .order_by('first_pull_request__closed_at').first().first_pull_request.closed_at
        last_pc_date = PairwiseConflict.objects.filter(first_pull_request__project=self.object)\
            .order_by('first_pull_request__closed_at').last().first_pull_request.closed_at

        pc_chart_data = (
            PairwiseConflict.objects.filter(first_pull_request__project=self.object)
                .annotate(date=TruncDay("first_pull_request__closed_at"))
                .values("date")
                .annotate(y=Count("id"))
                .order_by("-date")
        )

        # Serialize and attach the chart data to the template context
        pc_chart_data = json.dumps(list(pc_chart_data), cls=DjangoJSONEncoder)

        # IPE stats
        tws_ipe_stats = self.object.ipe_stats.all()

        # PRs info
        context['prs_number'] = prs_number
        context['merged_prs_number'] = merged_prs_number
        context['intra_branch_merged_prs_number'] = intra_branch_merged_prs_number
        context['first_pr_date'] = first_pr_date
        context['last_pr_date'] = last_pr_date
        context['pr_chart_data'] = pr_chart_data
        # Pairwise conflicts info
        context['pc_number'] = pc_number
        context['first_pc_date'] = first_pc_date
        context['last_pc_date'] = last_pc_date
        context['pc_chart_data'] = pc_chart_data
        # IPE Stats
        context['tws_ipe_stats'] = tws_ipe_stats

        return context
