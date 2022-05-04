# -*- coding: utf-8 -*-
import datetime
import csv
from django.core.management.base import BaseCommand, CommandError
from pairwise_conflict_dataset.models import Project, Commit
from pairwise_conflict_dataset import settings


class Command(BaseCommand):
    help = 'Import commits from a csv file'

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
            directory_path = settings.GHTORRENT_IMPORT_PATH + "/commits/"
        for project in projects.filter(commits__isnull=True).order_by('created_at'):
            file_path = directory_path + "{}_commits.csv".format(project.name.lower().replace('-', '_').replace('.', '_'))
            with open(file_path, 'r') as commits_file:
                reader = csv.DictReader(commits_file)
                for commit_dict in reader:
                    if not Commit.objects.filter(ghtorrent_id=commit_dict.get('id')).exists():
                        Commit.objects.create(ghtorrent_id=commit_dict.get('id'),
                                              project=project,
                                              sha=commit_dict.get('sha'),
                                              created_at=datetime.datetime.strptime(commit_dict.get('created_at'),
                                                                                    '%Y-%m-%d %H:%M:%S'),
                                              raw_data=commit_dict)
