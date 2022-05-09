# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from pairwise_conflict_dataset.models import Project
from ipe_analysis.models import ProjectIPEStats


class Command(BaseCommand):
    help = 'Get pairwise conflicts'

    def add_arguments(self, parser):
        parser.add_argument('--project_name', help="run command for one project")
        parser.add_argument('--tw_size', help="time window size")

    def handle(self, *args, **options):
        if options.get('project_name'):
            projects = Project.objects.filter(name=options.get('project_name'))
        else:
            projects = Project.objects.all()
        if options.get('tw_size'):
            tw_size = options.get('tw_size')
        else:
            tw_size = 14
        for project in projects:
            tw_quantity = project.ipe_time_windows.filter(tw_size=tw_size).count()
            tw_with_pc_quantity = project.ipe_time_windows.filter(tw_size=tw_size,
                                                                  pairwise_conflicts_number__gt=0).count()
            tw_with_pc_percentage = (tw_with_pc_quantity / tw_quantity) * 100
            tw_improves_ipe_quantity = project.ipe_time_windows.filter(tw_size=tw_size,
                                                                       pairwise_conflicts_number__gt=0,
                                                                       ipe_improvement_percentage__gt=0).count()
            tw_equal_ipe_quantity = project.ipe_time_windows.filter(tw_size=tw_size,
                                                                    pairwise_conflicts_number__gt=0,
                                                                    ipe_improvement_percentage=0).count()
            tw_not_improves_ipe_quantity = project.ipe_time_windows.filter(tw_size=tw_size,
                                                                           pairwise_conflicts_number__gt=0,
                                                                           ipe_improvement_percentage__lt=0).count()
            project_ipe_stats = ProjectIPEStats.objects.create(project=project,
                                                               tw_size=tw_size,
                                                               tw_quantity=tw_quantity,
                                                               tw_with_pc_percentage=tw_with_pc_percentage,
                                                               tw_improves_ipe_quantity=tw_improves_ipe_quantity,
                                                               tw_equal_ipe_quantity=tw_equal_ipe_quantity,
                                                               tw_not_improves_ipe_quantity=tw_not_improves_ipe_quantity
                                                               )
            # generate images
            project_ipe_stats.tw_without_pc_hist()
            project_ipe_stats.tw_with_pc_hist()
            project_ipe_stats.tw_with_pc_corr_matrix()
            project_ipe_stats.tw_with_pc_boxplot_conflict_resolutions()
