import datetime
import csv

from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import authentication, permissions

from pull_request_conflicts.ghtorrent import GHTorrentDB
from pull_request_conflicts.conflict_analyzer import PairwiseConflictGraphAnalyzer


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

        MAX_COLORS = 7

        table_name = '{}_pull_requests'.format(project_name)
        ghtorrent_db = GHTorrentDB(table_name)
        
        pairwise_conflict_by_pull_request = self.get_pairwise_conflict_by_pull_request(project_name)
        conflict_by_pull_request = self.get_conflict_by_pull_requests(project_name)

        labels = [a_date.strftime('%Y-%m-%d') for a_date in periods] 
        
        pr_amounts = []
        merged_pr_amounts = []
        not_merged_pr_amounts = []
        conflicting_pr_amounts = []
        pairwise_conflict_amounts = []
        real_conflict_amounts = []
        pull_request_groups_amounts = []
        pull_request_groups_by_period = []

        for idx in range(len(periods) - 1):
            a_date_from = periods[idx]
            a_date_to = periods[idx + 1]

            pr_amounts.append(ghtorrent_db.count_of_pull_requests_between(a_date_from, a_date_to))
            merged_pr_amounts.append(ghtorrent_db.count_of_merged_pull_requests_between(a_date_from, a_date_to))
            not_merged_pr_amounts.append(ghtorrent_db.count_of_not_merged_pull_requests_between(a_date_from, a_date_to))

            conflicting_pr_amount = 0
            pairwise_conflict_amount = 0
            real_conflict_amount = 0
            pull_request_groups = 0

            pull_requests = ghtorrent_db.get_pull_requests_between(a_date_from, a_date_to)
            pull_request_ids = [str(pr.pullreq_id) for pr in pull_requests]

            for pull_request_id in pull_request_ids:
                pairwise_conflicts = pairwise_conflict_by_pull_request.get(pull_request_id, [])
                pairwise_conflicts = list(filter(lambda x: x in pull_request_ids, pairwise_conflicts))
                pairwise_conflict_amount += len(pairwise_conflicts)
                if len(pairwise_conflicts) > 0:
                    conflicting_pr_amount += 1
                real_conflict_amount += conflict_by_pull_request.get(pull_request_id, 0)

            conflicting_pr_amounts.append(conflicting_pr_amount)
            pairwise_conflict_amounts.append(int(pairwise_conflict_amount/2))
            real_conflict_amounts.append(real_conflict_amount)

            graph = PairwiseConflictGraphAnalyzer(project_name, pull_requests)
            pull_request_groups = graph.get_groups_weight()
            pull_request_groups_amounts.append(len(pull_request_groups))
            pull_request_groups_by_period.append(pull_request_groups + [0] * (MAX_COLORS - len(pull_request_groups)))

        pull_request_groups_by_datasets = []
        for i in range(MAX_COLORS):
            pull_request_groups_by_dataset = []
            for groups in pull_request_groups_by_period:
                pull_request_groups_by_dataset.append(groups[i])
            pull_request_groups_by_datasets.append(pull_request_groups_by_dataset)

        response = {'labels': labels,
                    'pr_amounts': pr_amounts,
                    'merged_pr_amounts': merged_pr_amounts,
                    'not_merged_pr_amounts': not_merged_pr_amounts,
                    'conflicting_pr_amounts': conflicting_pr_amounts,
                    'pairwise_conflict_amounts': pairwise_conflict_amounts,
                    'real_conflict_amounts': real_conflict_amounts,
                    'pull_request_groups_amounts': pull_request_groups_amounts,
                    'pull_request_groups_by_datasets': pull_request_groups_by_datasets
                    }

        return Response(response)

    def get_pairwise_conflict_by_pull_request(self, project_name):
        filename = '/home/aolmedo/phd/repo/pull-request-conflicts/data/{}_pairwise_conflict_by_pull_request.csv'.format(project_name)

        pairwise_conflict_by_pull_request = {}

        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                pr_key = row[0]
                if row[1]:
                    pr_value = row[1].split(',')
                else:
                    pr_value = []
                pairwise_conflict_by_pull_request[pr_key] = pr_value

        return pairwise_conflict_by_pull_request

    def get_conflict_by_pull_requests(self, project_name):
        filename = '/home/aolmedo/phd/repo/pull-request-conflicts/data/{}_pull_request_conflict.csv'.format(project_name)

        pull_request_conflicts = {}

        with open(filename, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                pr_key = row[0]
                pr_value = int(row[1])
                pull_request_conflicts[pr_key] = pr_value

        return pull_request_conflicts

            
