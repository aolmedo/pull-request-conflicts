# -*- coding: utf-8 -*-
import datetime
from .conflict_analyzer import PairwiseConflictAnalyzer


if __name__ == "__main__":

    date_from = datetime.date(2010, 8, 30)
    date_to = datetime.date(2018, 8, 30)

    #date_from = datetime.date(2016, 2, 1)
    #date_to = datetime.date(2016, 3, 1)

    # gradle_conflict_analyzer = PairwiseConflictAnalyzer(project_name='broadleaf',
    #                                                     repo_path='/home/aolmedo/phd/projects/BroadleafCommerce',
    #                                                     repo_head='develop-6.0.x')
    # gradle_conflict_analyzer.export_pairwise_conflict_table(date_from, date_to)

    # gradle_conflict_analyzer = PairwiseConflictAnalyzer(project_name='gradle',
    #                                                     repo_path='/home/aolmedo/phd/projects/gradle',
    #                                                     repo_head='master')
    # gradle_conflict_analyzer.export_pairwise_conflict_table(date_from, date_to)

    # gradle_conflict_analyzer = PairwiseConflictAnalyzer(project_name='ruby',
    #                                                     repo_path='/home/aolmedo/phd/projects/rails',
    #                                                     repo_head='master')
    # gradle_conflict_analyzer.analyze()

    # gradle_conflict_analyzer = PairwiseConflictAnalyzer(project_name='elasticsearch',
    #                                                 repo_path='/home/aolmedo/phd/projects/elasticsearch',
    #                                                 repo_head='master')
    # gradle_conflict_analyzer.export_pairwise_conflict_table(date_from, date_to)

    # gradle_conflict_analyzer = PairwiseConflictAnalyzer(project_name='django',
    #                                             repo_path='/home/aolmedo/phd/projects/django',
    #                                             repo_head='master')
    # gradle_conflict_analyzer.export_pairwise_conflict_table(date_from, date_to)

    # gradle_conflict_analyzer = PairwiseConflictAnalyzer(project_name='react',
    #                                             repo_path='/home/aolmedo/phd/projects/react',
    #                                             repo_head='master')
    # gradle_conflict_analyzer.export_pairwise_conflict_table(date_from, date_to)

    gradle_conflict_analyzer = PairwiseConflictAnalyzer(project_name='twitter4j',
                                                        repo_path='/home/aolmedo/phd/projects/Twitter4J',
                                                        repo_head='master')
    gradle_conflict_analyzer.export_pairwise_conflict_by_pull_request(date_from, date_to)
