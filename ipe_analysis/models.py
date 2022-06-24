import io
import math
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
from django.db import models
from django.core.files.base import ContentFile
from django.utils.translation import gettext_lazy as _
from pairwise_conflict_dataset.models import Project
from pull_request_prioritization.pairwise_conflict_analyzer import PairwiseConflictGraphAnalyzer


class IPETimeWindow(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT,
                                verbose_name="project", related_name='ipe_time_windows')
    start_date = models.DateTimeField(_(u'start date'))
    end_date = models.DateTimeField(_(u'end date'))
    tw_size = models.PositiveIntegerField(_(u'time window size'), default=14)
    pull_requests_number = models.PositiveIntegerField(_(u'# merged PRs'))
    pairwise_conflicts_number = models.PositiveIntegerField(_(u'# pairwise conflicts'))
    potential_conflict_resolutions_number = models.PositiveIntegerField(_(u'# potential conflict resolutions'))
    unconflicting_pull_request_groups_number = models.PositiveIntegerField(_(u'# unconflicting PR groups'))
    historical_conflict_resolutions_number = models.PositiveIntegerField(_(u'# historical conflict resolutions'))
    historical_ipe = models.DecimalField(_(u'historical IPE '), max_digits=10, decimal_places=2)
    optimized_conflict_resolutions_number = models.PositiveIntegerField(_(u'# optimized conflict resolutions'))
    optimized_ipe = models.DecimalField(_(u'optimized IPE'), max_digits=10, decimal_places=2)
    ipe_improvement_percentage = models.DecimalField(_(u'IPE improvement (%)'), max_digits=10, decimal_places=2)
    cr_improvement_percentage = models.DecimalField(_(u'# conflict resolutions improvement (%)'),
                                                    max_digits=10, decimal_places=2)
    # images
    pairwise_conflict_graph_image = models.ImageField(upload_to='pairwise_conflict_graphs', null=True, blank=True)
    colored_pairwise_conflict_graph_image = models.ImageField(upload_to='colored_pairwise_conflict_graphs',
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


class ProjectIPEStats(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT,
                                verbose_name="project", related_name='ipe_stats')
    tw_size = models.PositiveIntegerField(_(u'time window size'), default=14)
    tw_quantity = models.PositiveIntegerField(_(u'# time windows'))
    tw_with_pc_percentage = models.DecimalField(_(u'% time windows with pairwise conflicts'),
                                                max_digits=10, decimal_places=2)
    tw_improves_ipe_quantity = models.PositiveIntegerField(_(u'# time windows improve IPE'))
    tw_equal_ipe_quantity = models.PositiveIntegerField(_(u'# time windows equal IPE'))
    tw_worsen_ipe_quantity = models.PositiveIntegerField(_(u'# time windows not improve IPE'))

    tw_improves_cr_quantity = models.PositiveIntegerField(_(u'# time windows improve CR number'))
    tw_equal_cr_quantity = models.PositiveIntegerField(_(u'# time windows equal CR number'))

    cr_improvement_percentage_min = models.DecimalField(_(u'MIN # conflict resolutions improvement (%)'),
                                                        max_digits=10, decimal_places=2)
    cr_improvement_percentage_mean = models.DecimalField(_(u'MEAN # CR improvement (%)'),
                                                         max_digits=10, decimal_places=2)
    cr_improvement_percentage_std = models.DecimalField(_(u'STD # CR improvement (%)'),
                                                        max_digits=10, decimal_places=2)
    cr_improvement_percentage_max = models.DecimalField(_(u'MAX # CR improvement (%)'),
                                                        max_digits=10, decimal_places=2)

    ipe_improvement_percentage_min = models.DecimalField(_(u'MIN IPE improvement (%)'),
                                                         max_digits=10, decimal_places=2)
    ipe_improvement_percentage_mean = models.DecimalField(_(u'MEAN IPE improvement (%)'),
                                                         max_digits=10, decimal_places=2)
    ipe_improvement_percentage_std = models.DecimalField(_(u'STD IPE improvement (%)'),
                                                        max_digits=10, decimal_places=2)
    ipe_improvement_percentage_max = models.DecimalField(_(u'MAX IPE improvement (%)'),
                                                         max_digits=10, decimal_places=2)

    def tw_without_pc_quantity(self):
        return self.project.ipe_time_windows.filter(tw_size=self.tw_size,
                                                    pairwise_conflicts_number=0).count()

    def tw_with_pc_quantity(self):
        return self.project.ipe_time_windows.filter(tw_size=self.tw_size,
                                                    pairwise_conflicts_number__gt=0).count()

    def tw_without_pc_dataframe(self):
        tws = self.project.ipe_time_windows.filter(tw_size=self.tw_size,
                                                   pairwise_conflicts_number=0)
        df = pd.DataFrame.from_records(list(tws.values()), coerce_float=True)
        if len(df) > 0:
            df = df.drop(columns=['id', 'project_id', 'start_date', 'end_date', 'tw_size', 'pairwise_conflict_graph_image',
                                  'colored_pairwise_conflict_graph_image', 'pull_request_group_graph_image',
                                  'integration_trajectories_image'])
        return df

    def tw_with_pc_dataframe(self):
        tws = self.project.ipe_time_windows.filter(tw_size=self.tw_size,
                                                   pairwise_conflicts_number__gt=0)
        df = pd.DataFrame.from_records(list(tws.values()),  coerce_float=True)
        if len(df) > 0:
            df = df.drop(columns=['id', 'project_id', 'start_date', 'end_date', 'tw_size', 'pairwise_conflict_graph_image',
                                  'colored_pairwise_conflict_graph_image', 'pull_request_group_graph_image',
                                  'integration_trajectories_image'])
            # df['cr_improvement_percentage'] = [((tw.historical_conflict_resolutions_number /
            #                                     tw.optimized_conflict_resolutions_number) - 1) * 100.0 for tw in tws]
        return df

    def tw_with_pc_stats(self):
        df = self.tw_with_pc_dataframe()
        if df.empty:
            return df
        desc = df.describe()
        desc = desc.drop(["count", "25%", "50%", "75%"])
        return desc

    def fill_statistical_data(self):
        stats = self.tw_with_pc_stats()
        if not stats.empty:
            self.cr_improvement_percentage_min = stats["cr_improvement_percentage"]["min"]
            self.cr_improvement_percentage_mean = stats["cr_improvement_percentage"]["mean"]
            self.cr_improvement_percentage_std = stats["cr_improvement_percentage"]["std"]
            self.cr_improvement_percentage_max = stats["cr_improvement_percentage"]["max"]
            self.ipe_improvement_percentage_min = stats["ipe_improvement_percentage"]["min"]
            self.ipe_improvement_percentage_mean = stats["ipe_improvement_percentage"]["mean"]
            self.ipe_improvement_percentage_std = stats["ipe_improvement_percentage"]["std"]
            self.ipe_improvement_percentage_max = stats["ipe_improvement_percentage"]["max"]

    def multiple_correlation(self, x, y, z):
        """
            Independent variables: x and y

            Dependent variable: z
        """
        # https://stackoverflow.com/questions/55369159/how-to-perform-three-variable-correlation-with-python-pandas
        df = self.tw_with_pc_dataframe()
        if df.empty:
            return
        cor = df.corr()

        # Pairings
        xz = cor.loc[x, z]
        yz = cor.loc[y, z]
        xy = cor.loc[x, y]

        Rxyz = math.sqrt((abs(xz ** 2) + abs(yz ** 2) - 2 * xz * yz * xy) / (1 - abs(xy ** 2)))
        R2 = Rxyz ** 2

        # Calculate adjusted R-squared
        n = len(df)  # Number of rows
        k = 2  # Number of independent variables
        R2_adj = 1 - (((1 - R2) * (n - 1)) / (n - k - 1))
        return R2, R2_adj

    def __str__(self):
        return "{} IPE stats".format(self.project.name)

    class Meta:
        ordering = ["project__created_at", "tw_size"]
        verbose_name = _("project IPE stats")
        verbose_name_plural = _(u"projects IPE stats")


class IPECalculation(object):

    def __init__(self, project, date_from, date_to):
        self.project = project
        self.pull_requests = self.project.pull_requests.filter(merged=True,
                                                               closed_at__gte=date_from,
                                                               closed_at__lte=date_to).order_by('closed_at')
        if self.pull_requests:
            self.pcga = PairwiseConflictGraphAnalyzer(self.project, self.pull_requests)
            self.historical_conflict_resolutions_number = 0
            self.optimized_conflict_resolutions_number = len(self.pcga.groups) - 1
            self.historical_ipe = self.get_historical_ipe()
            self.optimized_ipe = self.get_optimized_ipe()
            self.ipe_improvement_percentage = ((self.optimized_ipe / self.historical_ipe) - 1) * 100
            if self.optimized_conflict_resolutions_number > 0:
                self.cr_improvement_percentage = ((self.historical_conflict_resolutions_number /
                                                   self.optimized_conflict_resolutions_number) - 1) * 100
            else:
                self.cr_improvement_percentage = 0

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
                     xy=(((max_x + 1) + ((max_x + 1) * 0.1)) / 2, ((max_y + 1) / 2) + ((max_y + 1) * 0.1)),
                     color="b", fontsize=10, weight="bold")
        plt.annotate("IPE = {}".format(self.optimized_ipe),
                     xy=((max_x + 1) * 0.1, ((max_y + 1)/2) + ((max_y+1) * 0.1)),
                     color="r", fontsize=10, weight="bold")
        plt.savefig(figure, format='png')
        plt.clf()
        return figure
