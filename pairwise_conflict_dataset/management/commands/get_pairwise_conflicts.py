# -*- coding: utf-8 -*-
import time

from django.core.management.base import BaseCommand, CommandError
from pairwise_conflict_dataset.models import Project, PullRequest, PairwiseConflict
from pairwise_conflict_dataset.git_cmd import GitCommandLineInterface


class Command(BaseCommand):
    git_cmd = None
    help = 'Get pairwise conflicts'

    def add_arguments(self, parser):
        parser.add_argument('--project_name', help="run command for one project")

    def handle(self, *args, **options):
        if options.get('project_name'):
            projects = Project.objects.filter(name=options.get('project_name'))
        else:
            projects = Project.objects.all()

        for project in projects.filter(pairwise_conflicts_count__lte=0).order_by('created_at'):
            self.git_cmd = GitCommandLineInterface(project)
            self.git_cmd.clone()
            total_prs = 0
            total_fail_prs = 0
            for pull_request in project.pull_requests.filter(merged=True,
                                                             first_pairwise_conflicts__isnull=True,
                                                             second_pairwise_conflicts__isnull=True)\
                    .order_by('opened_at'):
                total_prs += 1
                for another_pull_request in PullRequest.objects.filter(merged=True,
                                                                       closed_at__gte=pull_request.opened_at,
                                                                       closed_at__lte=pull_request.closed_at)\
                        .order_by('opened_at'):
                    conflict_ret = self.conflicting_pull_requests(pull_request, another_pull_request)
                    if conflict_ret == -1:
                        total_fail_prs += 1
                        break;
                    if conflict_ret > 0:
                        PairwiseConflict.objects.create(first_pull_request=pull_request,
                                                        second_pull_request=another_pull_request)

                for another_pull_request in PullRequest.objects.filter(merged=True,
                                                                       opened_at__gte=pull_request.opened_at,
                                                                       opened_at__lte=pull_request.closed_at)\
                        .order_by('opened_at'):
                    conflict_ret = self.conflicting_pull_requests(pull_request, another_pull_request)
                    if conflict_ret == -1:
                        break;
                    if conflict_ret > 0:
                        PairwiseConflict.objects.create(first_pull_request=pull_request,
                                                        second_pull_request=another_pull_request)
                print("Cantidad de PRs: ", total_prs)
                print("Cantidad de PRs fallados: ", total_fail_prs)
                print("calidad: ", (1 - (total_fail_prs/total_prs)) * 100.0)

    def conflicting_pull_requests(self, a_pull_request, another_pull_request):
        ret = 0
        if a_pull_request.base_branch != another_pull_request.base_branch:
            return ret

        if PairwiseConflict.objects.filter(first_pull_request=a_pull_request,
                                           second_pull_request=another_pull_request).exists() or \
                PairwiseConflict.objects.filter(first_pull_request=another_pull_request,
                                                second_pull_request=a_pull_request).exists():
            return ret

        # print("Merge entre PR #{} y PR #{}".format(a_pull_request.github_id, another_pull_request.github_id))

        a_pull_request_commit = a_pull_request.head_commit
        another_pull_request_commit = another_pull_request.head_commit

        if a_pull_request_commit and another_pull_request_commit:
            commit_sha_1 = a_pull_request_commit.sha
            commit_sha_2 = another_pull_request_commit.sha

            # print("Merge de commit {} en el commit {}".format(commit_sha_2, commit_sha_1))

            ret = int(self.git_cmd.conflicting_merge(commit_sha_1, commit_sha_2))

        return ret
