# -*- coding: utf-8 -*-

if __name__ == "__main__":
    import datetime
    from .conflict_analyzer import PullRequestConflictAnalyzer

    date_from = datetime.date(2012, 1, 1)
    date_to = datetime.date(2019, 6, 1)

    gradle_conflict_analyzer = PullRequestConflictAnalyzer(project_name='broadleaf',
                                                          repo_path='/home/aolmedo/phd/projects/BroadleafCommerce',
                                                          repo_head='develop-6.0.x')
    gradle_conflict_analyzer.export_pull_request_conflict_table(date_from, date_to)

    # qgis_conflict_analyzer = PullRequestConflictAnalyzer(project_name='qgis',
    #                                                        repo_path='/home/aolmedo/phd/projects/QGIS',
    #                                                        repo_head='master')
    # qgis_conflict_analyzer.analyze()

    # django_conflict_analyzer = PullRequestConflictAnalyzer(project_name='django',
    #                                                        repo_path='/home/aolmedo/phd/projects/django',
    #                                                        repo_head='master')
    # django_conflict_analyzer.analyze()

    # django_conflict_analyzer = PullRequestConflictAnalyzer(project_name='ruby',
    #                                                        repo_path='/home/aolmedo/phd/projects/rails',
    #                                                        repo_head='master')
    # django_conflict_analyzer.analyze()

    # django_conflict_analyzer = PullRequestConflictAnalyzer(project_name='broadleaf',
    #                                                        repo_path='/home/aolmedo/phd/projects/BroadleafCommerce',
    #                                                        repo_head='develop-6.0.x')
    # django_conflict_analyzer.export_pull_request_conflict_table()

    # django_conflict_analyzer = PullRequestConflictAnalyzer(project_name='elasticsearch',
    #                                                        repo_path='/home/aolmedo/phd/projects/elasticsearch',
    #                                                        repo_head='master')
    # django_conflict_analyzer.export_pull_request_conflict_table()