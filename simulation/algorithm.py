import numpy
import math

class Bin():
    def __init__(self, hypervisor, capacity):
        self.capacity = capacity
        self.hypervisor = hypervisor
        self.total_capacity = capacity
        self.elements = []

    def put(self, element):
        self.elements.append(element)
        self.capacity -= element.value

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

    def __repr__(self):
        return "[%s]" % ', '.join(map(str, self.baseband_units))

class Algorithm():
    DEBUG = True

    def get_assignment(topology):
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
            'residuals': residuals
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
                if (target_bin.capacity * target_utilization >= element.value):
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
