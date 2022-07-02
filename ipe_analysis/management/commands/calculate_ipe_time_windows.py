# -*- coding: utf-8 -*-
import datetime
from django.core.management.base import BaseCommand, CommandError
from django.core.files.base import ContentFile
from pairwise_conflict_dataset.models import Project, PairwiseConflict
from pull_request_prioritization.pairwise_conflict_analyzer import GraphDrawer
from ipe_analysis.models import IPETimeWindow, IPECalculation


class Command(BaseCommand):
    help = 'Calculate IPE Time Windows'

    def add_arguments(self, parser):
        parser.add_argument('--project_name', help="run command for one project")
        parser.add_argument('--time_interval', help="time window lenght")
        parser.add_argument('--generate_images', help="time window lenght")

    def handle(self, *args, **options):
        if options.get('project_name'):
            projects = Project.objects.filter(name=options.get('project_name'))
        else:
            projects = Project.objects.all()
        if options.get('time_interval'):
            time_interval = int(options.get('time_interval'))
        else:
            time_interval = 14
        if options.get('generate_images'):
            generate_images = True
        else:
            generate_images = False
        for project in projects:
            time_windows = []
            first_merged_pr = project.pull_requests.filter(merged=True).order_by('closed_at').first()
            current_date = first_merged_pr.closed_at.date()
            until_date = datetime.date(2019, 6, 1)  # GHTorrent last date

            while current_date < until_date:
                time_window = (current_date, current_date + datetime.timedelta(days=time_interval))
                time_windows.append(time_window)
                current_date = time_window[1]
            for time_window in time_windows:
                date_from = time_window[0]
                date_to = time_window[1]
                ipe_data = IPECalculation(project, date_from, date_to)
                if not ipe_data.pull_requests:
                    IPETimeWindow.objects.create(project=project, tw_size=time_interval,
                                                 start_date=date_from, end_date=date_to,
                                                 pull_requests_number=0,
                                                 pairwise_conflicts_number=0,
                                                 potential_conflict_resolutions_number=0,
                                                 unconflicting_pull_request_groups_number=0,
                                                 historical_conflict_resolutions_number=0,
                                                 historical_ipe=0,
                                                 optimized_conflict_resolutions_number=0,
                                                 optimized_ipe=0,
                                                 ipe_improvement_percentage=0,
                                                 cr_improvement_percentage=0)
                else:
                    ipe_time_window = IPETimeWindow.objects.create(project=project, tw_size=time_interval,
                                                                   start_date=date_from, end_date=date_to,
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
                                                                   ipe_improvement_percentage,
                                                                   cr_improvement_percentage=ipe_data.
                                                                   cr_improvement_percentage)
                    if generate_images:
                        file_name = '{}_{}_{}.png'.format(project.name,
                                                          date_from.strftime('%Y-%m-%d'),
                                                          date_to.strftime('%Y-%m-%d'))
                        blob = GraphDrawer().store_graph(ipe_data.pcga.convert_to_nx_graph(colored=False))
                        ipe_time_window.pairwise_conflict_graph_image.save(file_name, ContentFile(blob.getvalue()),
                                                                           save=True)

                        blob = GraphDrawer().store_graph(ipe_data.pcga.convert_to_nx_graph(colored=True))
                        ipe_time_window.colored_pairwise_conflict_graph_image.save(file_name,
                                                                                   ContentFile(blob.getvalue()),
                                                                                   save=True)

                        blob = GraphDrawer().store_graph(ipe_data.pcga.convert_pcgg_to_nx_graph(), height=1, width=1)
                        ipe_time_window.pull_request_group_graph_image.save(file_name, ContentFile(blob.getvalue()),
                                                                            save=True)

                        blob = ipe_data.plot()
                        ipe_time_window.integration_trajectories_image.save(file_name, ContentFile(blob.getvalue()),
                                                                            save=True)
