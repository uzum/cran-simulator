import numpy
import math
from collections import namedtuple

BBU_serialized = namedtuple('BBU_serialized', ['id'])
Hypervisor_serialized = namedtuple('Hypervisor_serialized', ['id'])

class Bin():
    def __init__(self, hypervisor, capacity):
        self.capacity = capacity
        self.hypervisor = hypervisor
        self.total_capacity = capacity
        self.elements = []

    def put(self, element):
        self.elements.append(element)
        self.capacity -= element.value

    def remove(self, element):
        self.elements.remove(element)
        self.capacity += element.value

    def serialize(self):
        return {
            'elements': [el.serialize() for el in self.elements],
            'hypervisor': self.hypervisor.id
        }

    def deserialize(state):
        obj = Bin(None, None)
        obj.elements = [Element.deserialize(el_state) for el_state in state['elements']]
        obj.hypervisor = Hypervisor_serialized(state['hypervisor'])
        return obj

    def __lt__(self, other):
        return self.capacity < other.capacity

    def __repr__(self):
        return 'Bin %d/%d [%s]' % (self.total_capacity - self.capacity, self.total_capacity, ', '.join(map(str, self.elements)))

class Element():
    def __init__(self, cluster, value):
        self.value = value
        self.cluster = cluster

    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self):
        return "Element %d" % (self.value)

    def __str__(self):
        return "Element %d" % (self.value)

    def serialize(self):
        return {
            'cluster': self.cluster.serialize()
        }

    def deserialize(state):
        return Element(Cluster.deserialize(state['cluster']), None)

class Cluster():
    def __init__(self, baseband_units = []):
        self.baseband_units = baseband_units

    def add(self, baseband_unit):
        self.baseband_units.append(baseband_unit)

    def has(self, baseband_unit):
        return baseband_unit in self.baseband_units

    def split(self):
        if (len(self.baseband_units) == 1):
            raise Exception("Cannot split a cluster with length 1")
        half = math.floor(len(self.baseband_units) / 2)
        return [
            Cluster(self.baseband_units[0:half]),
            Cluster(self.baseband_units[half:])
        ]

    def serialize(self):
        return {
            'baseband_units': [bbu.id for bbu in self.baseband_units]
        }

    def deserialize(state):
        return Cluster([BBU_serialized(bbu) for bbu in state['baseband_units']])

    def merge(clusters):
        merged = Cluster([])
        for cluster in clusters:
            merged.baseband_units.extend(cluster.baseband_units)
        return merged

    def __repr__(self):
        return "[%s]" % ', '.join(map(str, self.baseband_units))

class Algorithm():
    DEBUG = True

    def get_assignment_cost(topology, bins):
        total_received = 0
        for hypervisor in self.hypervisors:
            total_received += hypervisor.switch.packets_rec
        return total_received / self.external_switch.packets_rec

    def get_assignment(topology, algorithm):
        if algorithm == 'heuristic':
            return Algorithm.get_heuristic_assignment(topology)
        elif algorithm == 'normal':
            return Algorithm.get_normal_assignment(topology)
        elif algorithm == 'optimal':
            return Algorithm.get_optimal_assignment(topology)
        else:
            raise Exception('Undefined algorithm')

    def get_normal_assignment(topology):
        bins = list(map(lambda hypervisor: Bin(hypervisor, hypervisor.switch.rate), topology.hypervisors))
        elements = []
        residuals = []
        for hypervisor in topology.hypervisors:
            for bbu in hypervisor.bbus:
                cluster = Cluster([bbu])
                elements.append(Element(cluster, topology.get_cluster_load(cluster)))
        target_utilization = 0.50

        while(len(elements) > 0):
            result = Algorithm.best_fit_decreasing(bins, elements, target_utilization)
            bins = result['bins']
            elements = result['residuals']
            target_utilization += 0.25

        return {
            'bins': bins,
            'residuals': elements
        }

    def get_optimal_assignment(topology):
        bins = list(map(lambda hypervisor: Bin(hypervisor, hypervisor.switch.rate), topology.hypervisors))
        clusters = Algorithm.get_bbu_clusters(topology)
        elements = list(map(lambda cluster: Element(cluster, topology.get_cluster_load(cluster)), clusters))

        best_assignment = None
        best_assignment_load = float('inf')
        target_utilization = 0.75

        def recurse(bins, element_idx, placed_elements):
            nonlocal best_assignment
            nonlocal best_assignment_load

            if placed_elements == len(elements):
                load = 0
                for bin in bins:
                    joint_cluster = Cluster.merge([element.cluster for element in bin.elements])
                    load += topology.get_cluster_load(joint_cluster)

                if (load < best_assignment_load):
                    best_assignment = [bin.serialize() for bin in bins]
                    best_assignment_load = load

            for i in range(len(bins)):
                for j in range(element_idx, len(elements)):
                    if ((bins[i].total_capacity * (target_utilization - 1)) + bins[i].capacity >= elements[j].value):
                        bins[i].put(elements[j])
                        recurse(bins, j + 1, placed_elements + 1)
                        bins[i].remove(elements[j])

        while (best_assignment is None):
            recurse(bins, 0, 0)
            target_utilization += 0.25

        return {
            'bins': [Bin.deserialize(bin) for bin in best_assignment],
            'residuals': []
        }

    def get_heuristic_assignment(topology):
        bins = list(map(lambda hypervisor: Bin(hypervisor, hypervisor.switch.rate), topology.hypervisors))
        clusters = Algorithm.get_bbu_clusters(topology)
        elements = list(map(lambda cluster: Element(cluster, topology.get_cluster_load(cluster)), clusters))
        residuals = []

        target_utilization = 0.75
        while(len(elements) > 0):
            result = Algorithm.best_fit_decreasing(bins, elements, target_utilization)
            bins = result['bins']
            residuals = result['residuals']

            elements = []
            for element in residuals:
                if (len(element.cluster.baseband_units) > 1):
                    children = element.cluster.split()
                    elements.append(Element(children[0], topology.get_cluster_load(children[0])))
                    elements.append(Element(children[1], topology.get_cluster_load(children[1])))
            target_utilization += 0.1

        return {
            'bins': bins,
            'residuals': elements
        }

    def get_bbu_clusters(topology):
        bbus = {}
        for hypervisor in topology.hypervisors:
            for bbu in hypervisor.bbus:
                bbus[bbu.id] = bbu

        size = len(bbus)

        neighbor_matrix = numpy.zeros((size, size))

        for i in bbus:
            for j in bbus:
                neighbor_matrix[i][j] = topology.get_common_load(bbus[i], bbus[j])

        # for i in range(size):
        #     print('\t'.join(map(str, neighbor_matrix[i])))

        clusters = []
        for i in bbus:
            # analyzing for bbus[i]
            placed = False
            # if we have a cluster with a non-zero score neighbor, put it into that cluster
            for j in range(i):
                if j not in bbus: continue
                if i == j: continue

                if (neighbor_matrix[i][j] > 0):
                    # found a neighbor with a non-zero score
                    # find a cluster where this neighbor is present
                    for cluster in clusters:
                        if (cluster.has(bbus[j]) and not cluster.has(bbus[i])):
                            cluster.add(bbus[i])
                            placed = True
                            break
            # still not placed
            # - either there was no neighbor with positive score
            # - or no neighbor in a previously created cluster
            # time to create a new cluster
            if (placed is False):
                clusters.append(Cluster([bbus[i]]))

        return clusters

    def best_fit_decreasing(bins, elements, target_utilization):
        bins.sort()
        elements.sort(reverse=True)
        residuals = []

        for element in elements:
            found = False

            for idx in range(len(bins)):
                target_bin = bins[idx]
                if ((target_bin.total_capacity * (target_utilization - 1)) + target_bin.capacity >= element.value):
                    target_bin.put(element)
                    found = True
                    # if the element could be placed into the first bin
                    # we can break out of the loop directly
                    if (idx == 0):
                        break

                    # otherwise, bins should be re-ordered due to updated capacity
                    bins.remove(target_bin)
                    j_idx = idx
                    while bins[j_idx - 1].capacity > target_bin.capacity and j_idx > 0:
                        j_idx -= 1
                    bins.insert(j_idx, target_bin)
                    break

            # could not find a bin for this element
            # add it to the residuals for the next iteration
            if (not found):
                residuals.append(element)

        return {
            'bins': bins,
            'residuals': residuals
        }
