import datetime
import csv

from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import authentication, permissions

from pull_request_conflicts.ghtorrent import GHTorrentDB
from pull_request_conflicts.conflict_analyzer import PairwiseConflictAnalyzer, PairwiseConflictGraphAnalyzer


class PullRequestsDatasets(APIView):
    """
    View to list all users in the system.
    """
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        project_name = request.GET.get('project')
        date_from = request.GET.get('datefrom')
        date_to = request.GET.get('dateto')
        interval = request.GET.get('interval')  # daily, weekly, biweekly, monthly, annual

        date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d')
        date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d')

        time_interval_dict = {'daily': 1,
                              'weekly': 7,
                              'biweekly': 14,
                              'monthly': 30,
                              'annual': 364
                             }
        
        time_interval = time_interval_dict.get(interval, 1)

        periods = []

        current_date = date_from
        while current_date < date_to:
            periods.append(current_date)
            current_date = current_date + datetime.timedelta(days=time_interval)
        periods.append(date_to)

        table_name = '{}_pull_requests'.format(project_name)
        ghtorrent_db = GHTorrentDB(table_name)
        
        pairwise_conflict_analyzer = PairwiseConflictAnalyzer(project_name=project_name)
        pairwise_conflict_by_pull_request = pairwise_conflict_analyzer.get_pairwise_conflict_by_pull_request()

        labels = [a_date.strftime('%Y-%m-%d') for a_date in periods] 

        merged_pr_amounts = []
        conflicting_pr_amounts = []
        pairwise_conflict_amounts = []
        pull_request_groups_amounts = []
        pull_request_groups_by_period = []

        for idx in range(len(periods) - 1):
            a_date_from = periods[idx]
            a_date_to = periods[idx + 1]

            merged_pr_amounts.append(ghtorrent_db.count_of_merged_pull_requests_closed_between(a_date_from, a_date_to))

            conflicting_pr_amount = 0
            pairwise_conflict_amount = 0

            pull_requests = ghtorrent_db.get_merged_pull_requests_closed_between(a_date_from, a_date_to)
            pull_request_ids = [str(pr.pullreq_id) for pr in pull_requests]

            for pull_request_id in pull_request_ids:
                pairwise_conflicts = pairwise_conflict_by_pull_request.get(pull_request_id, [])
                pairwise_conflicts = list(filter(lambda x: x in pull_request_ids, pairwise_conflicts))
                pairwise_conflict_amount += len(pairwise_conflicts)
                if len(pairwise_conflicts) > 0:
                    conflicting_pr_amount += 1

            conflicting_pr_amounts.append(conflicting_pr_amount)
            pairwise_conflict_amounts.append(int(pairwise_conflict_amount/2))

            graph = PairwiseConflictGraphAnalyzer(project_name, pull_requests)
            pull_request_groups = graph.get_groups_weight()
            pull_request_groups_amounts.append(len(pull_request_groups))
            pull_request_groups_by_period.append(pull_request_groups)

        MAX_COLORS = max([len(group) for group in pull_request_groups_by_period])
        pull_request_groups_by_datasets = []
        for i in range(MAX_COLORS):
            pull_request_groups_by_dataset = []
            for groups in pull_request_groups_by_period:
                if i < len(groups):
                    pull_request_groups_by_dataset.append(groups[i])
                else:
                    pull_request_groups_by_dataset.append(0)
            pull_request_groups_by_datasets.append(pull_request_groups_by_dataset)

        response = {'labels': labels,
                    'merged_pr_amounts': merged_pr_amounts,
                    'conflicting_pr_amounts': conflicting_pr_amounts,
                    'pairwise_conflict_amounts': pairwise_conflict_amounts,
                    'pull_request_groups_amounts': pull_request_groups_amounts,
                    'pull_request_groups_by_datasets': pull_request_groups_by_datasets
                    }

        return Response(response)
