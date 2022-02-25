# -*- coding: utf-8 -*-
import time

from django.core.management.base import BaseCommand, CommandError
from pairwise_conflict_dataset.models import Project
from pairwise_conflict_dataset.github_api import GithubAPI


class Command(BaseCommand):
    help = 'Import commits from a csv file'

    def add_arguments(self, parser):
        # parser.add_argument('--directory_path', help="directory path")
        parser.add_argument('--project_name', help="run command for one project")
        parser.add_argument('--wait_at_limit', help="Wait an hour when limit is found")

    def handle(self, *args, **options):
        requests_count = 0
        if options.get('project_name'):
            projects = Project.objects.filter(name=options.get('project_name'))
        else:
            projects = Project.objects.all()
        for project in projects:
            for pull_request in project.pull_requests.filter(base_branch__isnull=True):
                print(pull_request.github_id)
                pr_json = GithubAPI.get_pull_request_info(pull_request)
                requests_count += 1
                base_branch = pr_json and pr_json.get('base') and pr_json.get('base').get('label') or ''
                print(pull_request.github_id, "->", base_branch)
                pull_request.base_branch = base_branch
                pull_request.save()
                if requests_count >= 5000:
                    if options.get('wait_at_limit'):
                        time.sleep(3601)
                        requests_count = 0
                    else:
                        return
