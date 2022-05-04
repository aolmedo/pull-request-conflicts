# -*- coding: utf-8 -*-
import datetime
import csv
from django.core.management.base import BaseCommand, CommandError
from pairwise_conflict_dataset.models import Project, Commit, PullRequest
from pairwise_conflict_dataset import settings


class Command(BaseCommand):
    help = 'Import pull requests from a csv file'

    def add_arguments(self, parser):
        parser.add_argument('--directory_path', help="directory path")
        parser.add_argument('--project_name', help="run command for one project")

    def handle(self, *args, **options):
        if options.get('project_name'):
            projects = Project.objects.filter(name=options.get('project_name'))
        else:
            projects = Project.objects.all()
        if options.get('directory_path'):
            directory_path = options.get('directory_path')
        else:
            directory_path = settings.GHTORRENT_IMPORT_PATH + "/pull_requests/"
        for project in projects.filter(pull_requests__isnull=True).order_by('created_at'):
            file_path = directory_path + "{}_pull_requests.csv".format(project.name.lower().replace('-', '_').replace('.', '_'))
            with open(file_path, 'r') as pull_requests_file:
                reader = csv.DictReader(pull_requests_file)
                for pull_request_dict in reader:
                    if not pull_request_dict.get('opened_at'):
                        continue;
                    if not PullRequest.objects.filter(ghtorrent_id=pull_request_dict.get('id')).exists():
                        base_commit = Commit.objects.filter(ghtorrent_id=pull_request_dict.get('base_commit_id') or 0)
                        base_commit = base_commit[0] if base_commit else None
                        head_commit = Commit.objects.filter(ghtorrent_id=pull_request_dict.get('head_commit_id') or 0)
                        head_commit = head_commit[0] if head_commit else None
                        PullRequest.objects.create(ghtorrent_id=pull_request_dict.get('id'),
                                                   project=project,
                                                   github_id=pull_request_dict.get('pullreq_id'),
                                                   base_commit=base_commit,
                                                   head_commit=head_commit,
                                                   intra_branch=(True if pull_request_dict.
                                                                 get('intra_branch') == 't' else False),
                                                   merged=(True if pull_request_dict.
                                                           get('merged') == 't' else False),
                                                   opened_at=datetime.datetime.strptime(pull_request_dict.
                                                                                        get('opened_at'),
                                                                                        '%Y-%m-%d %H:%M:%S'),
                                                   closed_at=(datetime.datetime.strptime(
                                                       pull_request_dict.get('closed_at'), '%Y-%m-%d %H:%M:%S')
                                                              if pull_request_dict.get('closed_at') else None),
                                                   raw_data=pull_request_dict)
