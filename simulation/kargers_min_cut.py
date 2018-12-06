import random
from copy import deepcopy

class Node(object):
    def __init__(self, id, neighbors = []):
        self.id = id
        self.neighbors = neighbors
        self.cluster = [self]

    def __repr__(self):
        return 'Node %s' % self.id

    def __str__(self):
        return 'Node %s' % self.id

class Graph(object):
    def __init__(self, nodes = []):
        self.nodes = nodes

    def size(self):
        return len(self.nodes)

    def __repr__(self):
        string = ''
        for node in self.nodes:
            string = string + ('%s | %s' % (node, ', '.join(map(str, node.neighbors)))) + '\n'
        return string

class KargersMinCut(object):
    def solve(adjacency_matrix, run_count = None):
        if (run_count == None):
            run_count = len(adjacency_matrix[0])

        nodes = [Node(i) for i in adjacency_matrix[0]]
        for node_i in nodes:
            for node_j in nodes:
                if (node_i == node_j) continue
                if (adjacency_matrix[node_i][node_j] > 0):
                    node_i.neighbors.append(node_j)

        graph = Graph(nodes)
        runs = []
        for run in range(0, run_count):
            runs.append(KargersMinCut.find_min_cut(deepcopy(graph)))
        best_run = runs[0]
        for run in runs[1:]:
            if (run['cutlength'] <= best_run['cutlength']):
                if (abs(len(run['alpha']) - len(run['beta'])) < abs(len(best_run['alpha']) - len(best_run['beta'])))
                    best_run = run
        return [best_run['alpha'], best_run['beta']]

    def find_min_cut(graph):
        while graph.size() > 2:
             v = random.choice(graph.nodes)
             w = random.choice(v.neighbors)
             contract(graph, v, w)

        return {
            'cutlength': len(graph.nodes[0].neighbors),
            'alpha': [node.id for node in graph.nodes[0].cluster],
            'beta': [node.id for node in graph.nodes[1].cluster]
        }

    def contract(graph, v, w):
        # remove w, extend v
        v.cluster.extend(w.cluster)
        for node in w.neighbors:
            if (node != v):
                v.neighbors.append(node)
            node.neighbors.remove(w)
            if (node != v):
                node.neighbors.append(v)
        graph.nodes.remove(w)
