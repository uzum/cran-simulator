class Bin():
    def __init__(self, capacity):
        self.capacity = capacity
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
    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        return self.value < other.value

    def __repr__(self):
        return "Element %d" % (self.value)

    def __str__(self):
        return "Element %d" % (self.value)

class Algorithm():
    def DEBUG = True

    def assign(bins, elements):
        return Algorithm.best_fit_decreasing(
            list(map(lambda capacity: Bin(capacity), bins)),
            list(map(lambda value: Element(value), elements))
        )

    def best_fit_decreasing(bins, elements):
        bins.sort()
        elements.sort(reverse=True)

        for element in elements:
            if (Algorithm.DEBUG):
                print('\n\n\nnew iteration, placing %d' % element.value)
                print('\n'.join(map(str, bins)))

            for idx in range(len(bins)):
                target_bin = bins[idx]
                if (target_bin.capacity >= element.value):
                    target_bin.put(element)
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

            if (Algorithm.DEBUG):
                print('bin list updated:')
                print('\n'.join(map(str, bins)))

        return bins
