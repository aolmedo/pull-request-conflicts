# -*- coding: utf-8 -*-
import subprocess
import csv
from pull_request_prioritization import settings


class PairwiseConflictGraphAnalyzer(object):

    def __init__(self, project, pull_requests):
        self.project = project
        self.pull_request_ids = [str(pr.github_id) for pr in pull_requests]
        self.edges = 0
        self.potential_conflicting_prs = 0
        self.conflict_matrix_path = settings.CONFLICT_MATRIX_PATH
        self.graph = self.make_graph(pull_requests)

    def make_graph(self, pull_requests):
        graph = []
        # Row
        for r, a_pull_request in enumerate(pull_requests):
            new_row = []
            # Column
            for c, another_pull_request in enumerate(pull_requests):
                if c == r:
                    value = 0
                elif c > r:  # get conflicts between PRs
                    if (a_pull_request.first_pairwise_conflicts.filter(
                            second_pull_request=another_pull_request).exists() or
                        a_pull_request.second_pairwise_conflicts.filter(
                            first_pull_request=another_pull_request).exists()):
                        value = 1
                    else:
                        value = 0
                    self.edges += value
                else:  # already calculated
                    value = graph[c][r]
                new_row.append(value)
            if sum(new_row) > 0:
                self.potential_conflicting_prs += 1
            graph.append(new_row)
        print(graph)
        return graph
                
    def get_groups_weight(self):
        self.save_graph()
        groups = []
        result = subprocess.run(['java','-jar', 'matrix.jar'],
                                cwd=self.conflict_matrix_path, capture_output=True)

        groups_str = result.stdout.decode('utf-8').split('\n')[:-1]
        for group_str in groups_str:
            groups.append(group_str.split(','))

        return [len(group) for group in groups]

    def save_graph(self):
        filename = '{}/matrix.csv'.format(self.conflict_matrix_path)
        with open(filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['0'] + self.pull_request_ids)
            for i in range(len(self.pull_request_ids)):
                csv_writer.writerow([self.pull_request_ids[i]] + self.graph[i])
