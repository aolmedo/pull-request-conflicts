# -*- coding: utf-8 -*-
import io
import subprocess
import csv
import pandas as pd
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
from pull_request_prioritization import settings


class PairwiseConflictGraphAnalyzer(object):

    def __init__(self, project, pull_requests):
        self.project = project
        self.pull_requests = pull_requests
        self.pull_request_ids = [str(pr.github_id) for pr in pull_requests]
        self.pairwise_conflict_number = 0
        self.groups = self.color_pairwise_conflict_graph()
        self.pairwise_conflict_number = 0
        self.pairwise_conflict_graph = self.make_pairwise_conflict_graph(pull_requests)
        self.potential_conflicting_prs_number = self.get_potential_conflicting_prs_number()
        self.pairwise_conflict_group_graph = self.make_pairwise_conflict_group_graph()
        self.optimal_integration_sequence = self.get_optimal_integration_sequence()

    def make_pairwise_conflict_graph(self, pull_requests):
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
                    self.pairwise_conflict_number += value
                else:  # already calculated
                    value = graph[c][r]
                new_row.append(value)
            graph.append(new_row)
        return graph

    def pr_with_conflict(self, a_pull_request):
        ret = False
        for another_pull_request in self.pull_requests:
            if (a_pull_request.first_pairwise_conflicts.filter(
                    second_pull_request=another_pull_request).exists() or
                    a_pull_request.second_pairwise_conflicts.filter(
                        first_pull_request=another_pull_request).exists()):
                ret = True
        return ret

    def color_pairwise_conflict_graph(self):
        conflict_matrix_path = settings.CONFLICT_MATRIX_PATH
        self.store_pairwise_conflict_graph(conflict_matrix_path)
        groups = []
        result = subprocess.run(['java', '-jar', 'matrix.jar'],
                                cwd=conflict_matrix_path, capture_output=True)

        groups_str = result.stdout.decode('utf-8').split('\n')[:-1]
        for group_str in groups_str:
            groups.append(group_str.split(','))
        prs_without_conflicts = [str(pr.github_id) for pr in self.pull_requests if not self.pr_with_conflict(pr)]
        if groups:
            groups[0] = groups[0] + prs_without_conflicts
        else:
            groups = [prs_without_conflicts]
        return groups

    def store_pairwise_conflict_graph(self, conflict_matrix_path):
        filename = '{}/matrix.csv'.format(conflict_matrix_path)
        prs_with_conflicts = [pr for pr in self.pull_requests if self.pr_with_conflict(pr)]
        _pairwise_conflict_graph = self.make_pairwise_conflict_graph(prs_with_conflicts)
        prs_with_conflicts_ids = [str(pr.github_id) for pr in prs_with_conflicts]
        with open(filename, 'w') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(['0'] + prs_with_conflicts_ids)
            for i in range(len(prs_with_conflicts_ids)):
                csv_writer.writerow([prs_with_conflicts_ids[i]] + _pairwise_conflict_graph[i])

    def make_pairwise_conflict_group_graph(self):
        graph = []
        # Row
        for r, a_group in enumerate(self.groups):
            new_row = []
            # Column
            for c, another_group in enumerate(self.groups):
                if c == r:
                    value = 0
                elif c > r:  # get conflicts between PR groups
                    value = 0
                    for a_pr in a_group:
                        for another_pr in another_group:
                            a_pr_idx = self.pull_request_ids.index(a_pr)
                            another_pr_idx = self.pull_request_ids.index(another_pr)
                            value += self.pairwise_conflict_graph[a_pr_idx][another_pr_idx]
                else:  # already calculated
                    value = graph[c][r]
                new_row.append(value)
            graph.append(new_row)
        return graph

    def get_groups_weight(self):
        return [len(group) for group in self.groups]

    def convert_to_nx_graph(self, colored=True):
        """
            Convert matrix to networkx graph
        """
        graph_dict = {}
        for i, pr_pairwise_conflicts in enumerate(self.pairwise_conflict_graph):
            pr_id = self.pull_request_ids[i]
            graph_dict[pr_id] = pr_pairwise_conflicts

        A = pd.DataFrame(graph_dict, index=self.pull_request_ids)

        G_nx = nx.from_pandas_adjacency(A, create_using=nx.Graph())
        G_nx.graph['edge'] = {'arrowsize': '1.0', 'splines': 'curved'}
        G_nx.graph['graph'] = {'scale': '3'}

        if colored:
            # red, green, blue, turquoise, sienna, purple, navy, teal, olive, maroon, dark golden rod, lime,
            # gray, dark orange, slate gray
            color_list = ['#FF0000', '#008000', '#0000FF', '#40e0d0', '#a0522d', '#800080', '#000080', '#008080',
                          '#808000', '#800000', '#B8860B', '#00FF00', '#808080', '#FF8C00', '#708090']
            for node, properties in G_nx.nodes(data=True):
                for i, group in enumerate(self.groups):
                    if node in group:
                        properties['style'] = 'filled'
                        properties['fontcolor'] = 'white'
                        properties['color'] = color_list[i]
                        properties['fillcolor'] = color_list[i]
                        break;
        return G_nx

    def get_potential_conflicting_prs_number(self):
        potential_conflicting_prs_number = 0
        g_nx = self.convert_to_nx_graph()
        cliques = [c for c in nx.enumerate_all_cliques(g_nx) if len(c) > 1]
        cliques.reverse()
        clique_counted = []
        for clique in cliques:
            subclique = False
            for c in clique_counted:
                if set(clique).issubset(set(c)):
                    subclique = True
            if not subclique:
                potential_conflicting_prs_number += len(clique)-1
                clique_counted.append(clique)
        return potential_conflicting_prs_number

    def convert_pcgg_to_nx_graph(self):
        """
            Convert matrix to networkx graph
        """
        graph_dict = {}
        for i, pr_group_pairwise_conflicts in enumerate(self.pairwise_conflict_group_graph):
            graph_dict[i] = pr_group_pairwise_conflicts

        A = pd.DataFrame(graph_dict, index=range(len(self.groups)))

        G_nx = nx.from_pandas_adjacency(A, create_using=nx.Graph())
        G_nx.graph['edge'] = {'arrowsize': '1.0', 'splines': 'curved'}
        G_nx.graph['graph'] = {'scale': '3'}

        # red, green, blue, turquoise, sienna, purple, navy, teal, olive, maroon, dark golden rod, lime,
        # gray, dark orange, slate gray
        color_list = ['#FF0000', '#008000', '#0000FF', '#40e0d0', '#a0522d', '#800080', '#000080', '#008080',
                      '#808000', '#800000', '#B8860B', '#00FF00', '#808080', '#FF8C00', '#708090']
        for node, properties in G_nx.nodes(data=True):
            properties['weight'] = len(self.groups[node])
            properties['label'] = 'Group {}: {}'.format(node, len(self.groups[node]))
            properties['style'] = 'filled'
            properties['fontcolor'] = 'white'
            properties['color'] = color_list[node]
            properties['fillcolor'] = color_list[node]
        for edge in G_nx.edges(data=True):
            edge[2]['label'] = edge[2]['weight']
        return G_nx

    def get_optimal_integration_sequence(self):
        integration_sequence = []
        g_nx = self.convert_pcgg_to_nx_graph()
        # select biggest node of G
        v = None
        max_node_size = 0
        for node, properties in g_nx.nodes(data=True):
            if properties["weight"] > max_node_size:
                v = node
                max_node_size = properties["weight"]
        if v:
            integration_sequence.append(v)
        else:
            integration_sequence.append(0)
        # traverse graph nodes starting with the biggest node
        for it in range(len(g_nx.nodes()) - 1):
            neighbors = list(g_nx.neighbors(v))
            for x in integration_sequence:
                if x in neighbors:
                    neighbors.remove(x)
            if neighbors:
                best_neighbor = None
                best_trade_off_value = 0
                for neighbor in neighbors:
                    node_size = g_nx.nodes(data=True)[neighbor]['weight']
                    edge_accum_weight = 0
                    for node in integration_sequence:
                        edge = g_nx.get_edge_data(node, neighbor)
                        edge_accum_weight += edge['weight']
                    trade_off_value = node_size / edge_accum_weight
                    if trade_off_value > best_trade_off_value:
                        best_neighbor = neighbor
                        best_trade_off_value = trade_off_value
                v = best_neighbor
                integration_sequence.append(v)
        return integration_sequence


class GraphDrawer(object):

    def store_graph(self, graph, height=0.5, width=0.5, fontsize=10):
        """
            Draw and store graph
        """
        imgbuf = io.BytesIO()

        Agraph_eg = to_agraph(graph)

        Agraph_eg.node_attr["height"] = height
        Agraph_eg.node_attr["width"] = width
        Agraph_eg.node_attr["shape"] = "circle"
        Agraph_eg.node_attr["fixedsize"] = "true"
        Agraph_eg.node_attr["fontsize"] = fontsize
        Agraph_eg.layout(prog="neato")
        Agraph_eg.draw(imgbuf, format='png')

        return imgbuf
