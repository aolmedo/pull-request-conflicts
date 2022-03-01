import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
# from rest_framework import authentication, permissions

from pairwise_conflict_dataset.models import Project, PullRequest
from pull_request_prioritization.pairwise_conflict_analyzer import PairwiseConflictGraphAnalyzer


class PullRequestsDatasets(APIView):
    """
    View to list pull requests data
    """
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [permissions.IsAdminUser]

    def get(self, request, format=None):
        """
        Return a list of all pull requests
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

        labels = [a_date.strftime('%Y-%m-%d') for a_date in periods] 

        merged_pr_amounts = []
        conflicting_pr_amounts = []
        pairwise_conflict_amounts = []
        pull_request_groups_amounts = []
        pull_request_groups_by_period = []

        project = Project.objects.get(name=project_name)
        pull_requests_qs = project.pull_requests.filter(merged=True)

        for idx in range(len(periods) - 1):
            a_date_from = periods[idx]
            a_date_to = periods[idx + 1]

            pull_requests_inner_qs = pull_requests_qs.filter(closed_at__gte = a_date_from, closed_at__lte = a_date_to)

            merged_pr_amounts.append(pull_requests_inner_qs.count())

            graph = PairwiseConflictGraphAnalyzer(project, pull_requests_inner_qs.all())
            conflicting_pr_amounts.append(graph.potential_conflicting_prs_number)
            pairwise_conflict_amounts.append(graph.pairwise_conflict_number)
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
