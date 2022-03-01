# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.core.files.images import ImageFile
from pairwise_conflict_dataset.models import Project
from pull_request_prioritization.pairwise_conflict_analyzer import GraphDrawer
from ipe_analysis.models import IPETimeWindow, IPECalculation


class Command(BaseCommand):
    help = 'Get pairwise conflicts'

    def add_arguments(self, parser):
        parser.add_argument('--project_name', help="run command for one project")
        parser.add_argument('--time_interval', help="time window lenght")

    def handle(self, *args, **options):
        if options.get('project_name'):
            projects = Project.objects.filter(name=options.get('project_name'))
        else:
            projects = Project.objects.all()
        if options.get('time_interval'):
            time_interval = options.get('time_interval')
        else:
            time_interval = 14
        for project in projects:
            time_windows = []
            current_date = project.created_at
            until_date = datetime.datetime(2019, 6, 1)  # TODO: project.updated_at
            while current_date < until_date:
                time_window = (current_date, current_date + datetime.timedelta(days=time_interval))
                time_windows.append(time_window)
                current_date = time_window[1]
            for time_window in time_windows:
                date_from = time_window[0]
                date_to = time_window[1]
                ipe_data = IPECalculation(project, date_from, date_to)
                ipe_time_window = IPETimeWindow.objects.create(project=project, start_date=date_from, end_date=date_to,
                                                               pull_requests_number=ipe_data.pull_requests.count(),
                                                               pairwise_conflicts_number=ipe_data.pcga.
                                                               pairwise_conflict_number,
                                                               potential_conflict_resolutions_number=ipe_data.pcga.
                                                               potential_conflicting_prs_number,
                                                               unconflicting_pull_request_groups_number=len(
                                                                   ipe_data.pcga.groups),
                                                               historical_conflict_resolutions_number=ipe_data.
                                                               historical_conflict_resolutions_number,
                                                               historical_ipe=ipe_data.historical_ipe,
                                                               optimized_conflict_resolutions_number=ipe_data.
                                                               optimized_conflict_resolutions_number,
                                                               optimized_ipe=ipe_data.optimized_ipe,
                                                               ipe_improvement_percentage=ipe_data.
                                                               ipe_improvement_percentage)
                file_name = '{}_{}_{}'.format(project.name,
                                              date_from.strftime('%Y-%m-%d'),
                                              date_to.strftime('%Y-%m-%d'))
                blob = GraphDrawer().store_graph(ipe_data.pcga.convert_to_nx_graph(colored=False))
                ipe_time_window.pairwise_conflict_graph_image.save(file_name, ImageFile(blob.get_value()), save=True)

                blob = GraphDrawer().store_graph(ipe_data.pcga.convert_to_nx_graph(colored=True))
                ipe_time_window.colored_pairwise_conflict_graph_image.save(file_name,
                                                                           ImageFile(blob.get_value()), save=True)

                blob = GraphDrawer().store_graph(ipe_data.pcga.convert_pcgg_to_nx_graph(), height=1, width=1)
                ipe_time_window.pull_request_group_graph_image.save(file_name, ImageFile(blob.get_value()), save=True)

                blob = ipe_data.plot()
                ipe_time_window.integration_trajectories_image.save(file_name, ImageFile(blob.get_value()), save=True)
