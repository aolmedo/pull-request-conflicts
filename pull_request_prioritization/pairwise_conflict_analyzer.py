# -*- coding: utf-8 -*-
import subprocess
import csv
import pandas as pd
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
from pull_request_prioritization import settings


class PairwiseConflictGraphAnalyzer(object):

    def __init__(self, project, pull_requests):
        self.project = project
        self.pull_request_ids = [str(pr.github_id) for pr in pull_requests]
        self.edges = 0
        self.potential_conflicting_prs = 0
        self.conflict_matrix_path = settings.CONFLICT_MATRIX_PATH
        self.graph = self.make_graph(pull_requests)
        self.groups = self.color_graph()

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
        return graph

    def color_graph(self):
        self.save_graph()
        groups = []
        result = subprocess.run(['java', '-jar', 'matrix.jar'],
                                cwd=self.conflict_matrix_path, capture_output=True)

        groups_str = result.stdout.decode('utf-8').split('\n')[:-1]
        for group_str in groups_str:
            groups.append(group_str.split(','))

        return groups

    def save_graph(self):
        filename = '{}/matrix.csv'.format(self.conflict_matrix_path)
        with open(filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['0'] + self.pull_request_ids)
            for i in range(len(self.pull_request_ids)):
                csv_writer.writerow([self.pull_request_ids[i]] + self.graph[i])

    def get_groups_weight(self):
        return [len(group) for group in self.groups]

    def convert_to_nx_graph(self, colored=True):
        """
            Convert matrix to networkx graph
        """
        graph_dict = {}
        for i, pr_pairwise_conflicts in enumerate(self.graph):
            pr_id = self.pull_request_ids[i]
            graph_dict[pr_id] = pr_pairwise_conflicts

        A = pd.DataFrame(graph_dict, index=self.pull_request_ids)

        G_nx = nx.from_pandas_adjacency(A, create_using=nx.Graph())
        G_nx.graph['edge'] = {'arrowsize': '1.0', 'splines': 'curved'}
        G_nx.graph['graph'] = {'scale': '3'}

        if colored:
            # red, green, blue, turquoise, sienna
            color_list = ['#FF0000', '#00FF00', '#0000FF', '#40e0d0', '#a0522d']
            for node, properties in G_nx.nodes(data=True):
                for i, group in enumerate(self.groups)  :
                    if node in group:
                        properties['style'] = 'filled'
                        properties['fontcolor'] = 'white'
                        properties['color'] = color_list[i]
                        properties['fillcolor'] = color_list[i]
                        break;
        return G_nx

    def draw_graph(self, graph):
        """
            Draw graph
        """
        Agraph_eg = to_agraph(graph)

        Agraph_eg.node_attr["height"] = 0.5
        Agraph_eg.node_attr["width"] = 0.5
        Agraph_eg.node_attr["shape"] = "circle"
        Agraph_eg.node_attr["fixedsize"] = "true"
        Agraph_eg.node_attr["fontsize"] = 8
        Agraph_eg.layout(prog="neato")
        Agraph_eg.draw('graph_eg2.png')

        return Agraph_eg
