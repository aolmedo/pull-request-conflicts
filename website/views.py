from django.shortcuts import render
from django.views.generic import TemplateView, DetailView
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
