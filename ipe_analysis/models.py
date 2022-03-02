import io
from matplotlib import pyplot as plt
from django.db import models
from django.utils.translation import gettext_lazy as _
from pairwise_conflict_dataset.models import Project
from pull_request_prioritization.pairwise_conflict_analyzer import PairwiseConflictGraphAnalyzer


class IPETimeWindow(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT,
                                verbose_name="project", related_name='ipe_time_windows')
    start_date = models.DateTimeField(_(u'time window start date'))
    end_date = models.DateTimeField(_(u'time window end date'))
    pull_requests_number = models.PositiveIntegerField(_(u'# pull requests'))
    pairwise_conflicts_number = models.PositiveIntegerField(_(u'# pairwise conflicts'))
    potential_conflict_resolutions_number = models.PositiveIntegerField(_(u'# potential conflict resolutions'))
    unconflicting_pull_request_groups_number = models.PositiveIntegerField(_(u'# unconflicting pull request groups'))
    historical_conflict_resolutions_number = models.PositiveIntegerField(_(u'historical conflict resolutions number'))
    historical_ipe = models.DecimalField(_(u'historical IPE '), max_digits=10, decimal_places=2)
    optimized_conflict_resolutions_number = models.PositiveIntegerField(_(u'optimized conflict resolutions number'))
    optimized_ipe = models.DecimalField(_(u'optimized IPE'), max_digits=10, decimal_places=2)
    ipe_improvement_percentage = models.DecimalField(_(u'IPE improvement (%)'), max_digits=10, decimal_places=2)
    # images
    pairwise_conflict_graph_image = models.ImageField(upload_to='pairwise_conflict_graphs', null=True, blank=True)
    colored_pairwise_conflict_graph_image = models.ImageField(upload_to='colores_pairwise_conflict_graphs',
                                                              null=True, blank=True)
    pull_request_group_graph_image = models.ImageField(upload_to='pull_request_group_graphs', null=True, blank=True)
    integration_trajectories_image = models.ImageField(upload_to='integration_trajectories_figures',
                                                       null=True, blank=True)

    def __str__(self):
        return "{} - case study: {}".format(self.project.name, self.id)

    class Meta:
        ordering = ["start_date"]
        verbose_name = _("IPE time window")
        verbose_name_plural = _(u"IPE time windows")


class IPECalculation(object):

    def __init__(self, project, date_from, date_to):
        self.project = project
        self.pull_requests = self.project.pull_requests.filter(merged=True,
                                                               closed_at__gte=date_from,
                                                               closed_at__lte=date_to).order_by('closed_at')
        if self.pull_requests:
            self.pcga = PairwiseConflictGraphAnalyzer(self.project, self.pull_requests)
            self.historical_conflict_resolutions_number = 0
            self.optimized_conflict_resolutions_number = len(self.pcga.groups)
            self.historical_ipe = self.get_historical_ipe()
            self.optimized_ipe = self.get_optimized_ipe()
            self.ipe_improvement_percentage = ((self.optimized_ipe / self.historical_ipe) - 1) * 100

    def historical_cost_gain_function(self):
        self.historical_conflict_resolutions_number = 0
        cost_gain_table = []
        already_integrated_prs = []
        cumulative_gain = 0
        cumulative_cost = 0
        for pull_request in self.pull_requests:
            cost = 0
            for merged_pr in already_integrated_prs:
                pos_pull_request = self.pcga.pull_request_ids.index(str(pull_request.github_id))
                pos_merged_pr = self.pcga.pull_request_ids.index(str(merged_pr.github_id))
                cost += self.pcga.pairwise_conflict_graph[pos_pull_request][pos_merged_pr]
            if cost > 0:
                self.historical_conflict_resolutions_number += 1
            cumulative_cost += cost
            cumulative_gain += 1
            cost_gain_table.append((cumulative_cost, cumulative_gain))
            already_integrated_prs.append(pull_request)
        return cost_gain_table

    def optimized_cost_gain_function(self):
        cost_gain_table = []
        already_integrated_pr_group_id = []
        cumulative_gain = 0
        cumulative_cost = 0
        for group_id in self.pcga.optimal_integration_sequence:
            cost = 0
            for integrated_group_id in already_integrated_pr_group_id:
                group = self.pcga.groups[group_id]
                integrated_group = self.pcga.groups[integrated_group_id]
                for pull_request_id in group:
                    for merged_pull_request_id in integrated_group:
                        pos_pull_request = self.pcga.pull_request_ids.index(pull_request_id)
                        pos_merged_pr = self.pcga.pull_request_ids.index(merged_pull_request_id)
                        cost += self.pcga.pairwise_conflict_graph[pos_pull_request][pos_merged_pr]
            cumulative_cost += cost
            cumulative_gain += len(self.pcga.groups[group_id])
            cost_gain_table.append((cumulative_cost, cumulative_gain))
            already_integrated_pr_group_id.append(group_id)
        return cost_gain_table

    def get_historical_ipe(self):
        return self._calculate_area(self.historical_cost_gain_function())

    def get_optimized_ipe(self):
        return self._calculate_area(self.optimized_cost_gain_function())

    def _calculate_area(self, cost_gain_table):
        area = 0
        if len(cost_gain_table) == 1:
            area = cost_gain_table[0][1]
        for i in range(len(cost_gain_table)-1):
            area += cost_gain_table[i][1] * (cost_gain_table[i+1][0] - cost_gain_table[i][0])
        if area == 0:
            area = cost_gain_table[-1][1]
        return area

    def plot(self):
        figure = io.BytesIO()

        historical_integration_sequence = self.historical_cost_gain_function()
        historical_integration_sequence_x = [x[0] for x in historical_integration_sequence]
        historical_integration_sequence_y = [x[1] for x in historical_integration_sequence]

        optimized_integration_sequence = self.optimized_cost_gain_function()
        optimized_integration_sequence_x = [x[0] for x in optimized_integration_sequence]
        optimized_integration_sequence_y = [x[1] for x in optimized_integration_sequence]

        max_x = max(historical_integration_sequence_x + optimized_integration_sequence_x)
        max_y = max(historical_integration_sequence_y + optimized_integration_sequence_y)

        plt.step(historical_integration_sequence_x, historical_integration_sequence_y, "bs-",
                 where="post", label='historical')
        plt.step(optimized_integration_sequence_x, optimized_integration_sequence_y, "rD-",
                 where="post", label='proposal')
        plt.grid()
        plt.xlabel("Cumulative cost")
        plt.ylabel("Cumulative gain")
        plt.title("Integration Trajectories")
        plt.legend(loc="right")
        plt.xlim(0, max_x+1)
        plt.ylim(0, max_y+1)
        plt.annotate("IPE = {}".format(self.historical_ipe),
                     xy=(max_x / 2, (max_y / 2) + 2),
                     color="b", fontsize=10, weight="bold")
        plt.annotate("IPE = {}".format(self.optimized_ipe),
                     xy=(1, (max_y/2)+2),
                     color="r", fontsize=10, weight="bold")
        plt.savefig(figure, format='png')
        plt.clf()
        return figure
