from django.core.management.base import BaseCommand, CommandError
from pairwise_conflict_dataset.models import Project


class Command(BaseCommand):
    help = 'Import projects from a csv file'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('poll_ids', nargs='+', type=int)

    def handle(self, *args, **options):
        pass