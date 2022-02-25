# -*- coding: utf-8 -*-
import datetime
import csv
from django.core.management.base import BaseCommand, CommandError
from pairwise_conflict_dataset.models import Project
from pairwise_conflict_dataset import settings


class Command(BaseCommand):
    help = 'Import projects from a csv file'

    def add_arguments(self, parser):
        parser.add_argument('--file_path', help="project.csv file path")

    def handle(self, *args, **options):
        if options.get('file_path'):
            file_path = options.get('file_path')
        else:
            file_path = settings.GHTORRENT_IMPORT_PATH + "/projects.csv"

        with open(file_path, 'r') as project_file:
            reader = csv.DictReader(project_file)
            for project_dict in reader:
                if not Project.objects.filter(ghtorrent_id=project_dict.get('id')).exists():
                    Project.objects.create(ghtorrent_id=project_dict.get('id'),
                                           name=project_dict.get('name'),
                                           description=project_dict.get('description'),
                                           github_url=project_dict.get('url').replace('https://api.github.com/repos/',
                                                                                      'https://github.com/'),
                                           api_url=project_dict.get('url'),
                                           language=project_dict.get('language'),
                                           created_at=datetime.datetime.strptime(project_dict.get('created_at'),
                                                                                 '%Y-%m-%d %H:%M:%S'),
                                           raw_data=project_dict)
