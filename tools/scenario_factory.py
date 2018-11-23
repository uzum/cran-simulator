import random
import math
import json
from .plot import plot

TARGET_CLUSTERS = 8
TARGET_CLUSTER_SIZE = 8
TARGET_NEIGHBOR_SIZE = 2
TARGET_ARRIVAL_RATE = 10.0
TARGET_PACKET_MEAN = 100
TARGET_PACKET_DEV = 20
HYPERVISORS = 5
random.seed()

def get_random(mean, min_value=0, max_value=float('inf')):
    min_value = max(min_value, math.floor(mean * 0.6))
    max_value = min(max_value, math.floor(mean * 1.4))
    return random.randint(min_value, max_value)

clusters = []
rrh_id = 0
for i in range(TARGET_CLUSTERS):
    cluster = []
    rrh_size = get_random(TARGET_CLUSTER_SIZE)
    for rrh in range(rrh_size):
        cluster.append({
            'id': rrh_id,
            'arrival_rate': get_random(TARGET_ARRIVAL_RATE),
            'packet_mean': get_random(TARGET_PACKET_MEAN),
            'packet_dev': get_random(TARGET_PACKET_DEV),
            'baseband_units': []
        })
        rrh_id += 1
    if (rrh_size <= 1): continue
    indexes = list(map(lambda rrh: rrh['id'], cluster))
    for rrh in cluster:
        neighbor_size = get_random(TARGET_NEIGHBOR_SIZE, max_value = len(cluster) - 2)
        print('trying to find %d neighbors in a cluster of size %d' % (neighbor_size, len(cluster)))
        while (len(rrh['baseband_units']) < neighbor_size):
            candidate = random.choice(indexes)
            if (candidate != rrh['id'] and candidate not in rrh['baseband_units']):
                rrh['baseband_units'].append(candidate)
            random.shuffle(indexes)
    clusters.append(cluster)

topology = {
    'remote_radio_heads': [],
    'hypervisors': [{
        'id': 0,
        'baseband_units': []
    }]
}

bbu_per_hypervisor = math.ceil(rrh_id / HYPERVISORS)
current_hypervisor = topology['hypervisors'][0]
for cluster in clusters:
    for rrh in cluster:
        topology['remote_radio_heads'].append(rrh)
        current_hypervisor['baseband_units'].append({ 'id': rrh['id'] })
        if (len(current_hypervisor['baseband_units']) == bbu_per_hypervisor):
            current_hypervisor = { 'id': current_hypervisor['id'] + 1, 'baseband_units': [] }
            topology['hypervisors'].append(current_hypervisor)

plot(topology, 'test.png')
