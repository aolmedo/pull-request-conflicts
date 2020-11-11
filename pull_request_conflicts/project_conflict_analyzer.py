# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from conflict_analyzer import PullRequestConflcitAnalyzer

    gradle_conflict_analyzer = PullRequestConflcitAnalyzer(project_name='gradle',
                                                           repo_path='/home/aolmedo/phd/projects/gradle',
                                                           repo_head='ghtorrent')
    gradle_conflict_analyzer.analyze()
