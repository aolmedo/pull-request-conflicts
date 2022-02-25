# -*- coding: utf-8 -*-
import time

from django.core.management.base import BaseCommand, CommandError
from pairwise_conflict_dataset.models import Project
from pairwise_conflict_dataset.github_api import GithubAPI


class Command(BaseCommand):
    help = 'Upgrade project info'

    def add_arguments(self, parser):
        parser.add_argument('--project_name', help="run command for one project")
        parser.add_argument('--wait_at_limit', help="Wait an hour when limit is found")

    def handle(self, *args, **options):
        requests_count = 0
        if options.get('project_name'):
            projects = Project.objects.filter(name=options.get('project_name'))
        else:
            projects = Project.objects.all()

        for project in projects.filter(default_branch__isnull=True):
                pr_json = GithubAPI.get_project_info(project)
                requests_count += 1
                default_branch = pr_json and pr_json.get('default_branch') or 'main'
                print(project.name, "->", default_branch)
                project.default_branch = default_branch
                project.save()
                if requests_count >= 5000:
                    if options.get('wait_at_limit'):
                        time.sleep(3601)
                        requests_count = 0
                    else:
                        return
