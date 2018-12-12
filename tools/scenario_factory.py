import random
import math
import json
import time
import argparse
#from plotters.topology import plot

parser = argparse.ArgumentParser()
parser.add_argument('--output')
parser.add_argument('--cluster')
parser.add_argument('--cluster_size')
parser.add_argument('--connected', default=False)
args = parser.parse_args()

# topology parameters
TARGET_CLUSTERS = int(args.cluster)
TARGET_CLUSTER_SIZE = int(args.cluster_size)
TARGET_NEIGHBOR_SIZE = 3
TARGET_ARRIVAL_RATE = 25.0
TARGET_PACKET_MEAN = 100
TARGET_PACKET_DEV = 20
HYPERVISORS = round(TARGET_CLUSTERS * 0.75)

# simulation parameters
SIMULATION_TIME = 500
STEP_TIME = 5
VIRTUAL_SWITCH_RATE = 40000
VIRTUAL_SWITCH_QLIMIT = 1000
EXTERNAL_TRANSMISSION_COST = 5
INTERNAL_TRANSMISSION_COST = 1
EXTERNAL_TRANSMISSION_COFACTOR = 0.0001
INTERNAL_TRANSMISSION_COFACTOR = 0.0001
SPLIT_ALGORITHM = 'kargers'

scenario = {
    'simulation': {},
    'topology': {
        'remote_radio_heads': [],
        'hypervisors': [{
            'id': 0,
            'baseband_units': []
        }]
    },
    'updates': {
        'load': []
    }
}

def get_random(mean, min_value=0, max_value=float('inf')):
    min_value = max(min_value, math.floor(mean * 0.5))
    max_value = min(max_value, math.floor(mean * 1.5))

    if (min_value >= max_value): return round(min_value)
    return random.randint(min_value, max_value)

def generate_parameters():
    scenario['simulation']['SIMULATION_TIME'] = SIMULATION_TIME
    scenario['simulation']['STEP_TIME'] = STEP_TIME
    scenario['simulation']['VIRTUAL_SWITCH_QLIMIT'] = VIRTUAL_SWITCH_QLIMIT
    scenario['simulation']['VIRTUAL_SWITCH_RATE'] = VIRTUAL_SWITCH_RATE
    scenario['simulation']['EXTERNAL_TRANSMISSION_COST'] = EXTERNAL_TRANSMISSION_COST
    scenario['simulation']['INTERNAL_TRANSMISSION_COST'] = INTERNAL_TRANSMISSION_COST
    scenario['simulation']['EXTERNAL_TRANSMISSION_COFACTOR'] = EXTERNAL_TRANSMISSION_COFACTOR
    scenario['simulation']['INTERNAL_TRANSMISSION_COFACTOR'] = INTERNAL_TRANSMISSION_COFACTOR
    scenario['simulation']['SPLIT_ALGORITHM'] = SPLIT_ALGORITHM

def generate_topology():
    clusters = []
    rrh_count = 0
    total_rrh_size = round(TARGET_CLUSTERS * TARGET_CLUSTER_SIZE)
    TARGET_ARRIVAL_RATE = round(((VIRTUAL_SWITCH_RATE * HYPERVISORS)) / (total_rrh_size * TARGET_PACKET_MEAN))
    for i in range(TARGET_CLUSTERS):
        cluster = []
        if (i == TARGET_CLUSTERS - 1):
            rrh_size = total_rrh_size - rrh_count
        else:
            rrh_size = get_random((total_rrh_size - rrh_count) / (TARGET_CLUSTERS - i))
        print('%d rrhs in cluster %d' % (rrh_size, i))
        for rrh in range(rrh_size):
            cluster.append({
                'id': rrh_count,
                'arrival_rate': get_random(TARGET_ARRIVAL_RATE),
                'packet_mean': get_random(TARGET_PACKET_MEAN),
                'packet_dev': get_random(TARGET_PACKET_DEV),
                'baseband_units': []
            })
            rrh_count += 1
        clusters.append(cluster)

        if (rrh_size <= 1):
            cluster[0]['baseband_units'].append(cluster[0]['id'])
            continue

        indexes = list(map(lambda rrh: rrh['id'], cluster))
        for rrh in cluster:
            neighbor_size = get_random(TARGET_NEIGHBOR_SIZE, max_value = len(cluster) - 2)
            while (len(rrh['baseband_units']) < neighbor_size):
                candidate = random.choice(indexes)
                if (candidate != rrh['id'] and candidate not in rrh['baseband_units']):
                    rrh['baseband_units'].append(candidate)
                random.shuffle(indexes)
            # append its serving station with the same id
            rrh['baseband_units'].append(rrh['id'])
        if (args.connected):
            if (i > 0):
                cluster[0]['baseband_units'].append(clusters[i-1][0]['id'])

    bbu_per_hypervisor = math.ceil(rrh_count / HYPERVISORS)
    current_hypervisor = scenario['topology']['hypervisors'][0]
    for cluster in clusters:
        for rrh in cluster:
            scenario['topology']['remote_radio_heads'].append(rrh)
            current_hypervisor['baseband_units'].append({ 'id': rrh['id'] })
            if (len(current_hypervisor['baseband_units']) == bbu_per_hypervisor):
                current_hypervisor = { 'id': current_hypervisor['id'] + 1, 'baseband_units': [] }
                scenario['topology']['hypervisors'].append(current_hypervisor)

#    plot(scenario['topology'], 'topology')
    print('rrh size: %d' % len(scenario['topology']['remote_radio_heads']))
    print('hypervisor size: %d' % len(scenario['topology']['hypervisors']))
    print('cluster size: %d' % TARGET_CLUSTERS)

def generate_load():
    rrh_size = len(scenario['topology']['remote_radio_heads'])
    for time in range(0, SIMULATION_TIME, STEP_TIME):
        effect_percent = get_random(20, 10, 30)
        affected_rrh_size = math.floor(effect_percent * rrh_size * 0.01)
        for rrh in random.sample(scenario['topology']['remote_radio_heads'], affected_rrh_size):
            new_arrival_rate = get_random(TARGET_ARRIVAL_RATE)
            scenario['updates']['load'].append({
                'time': time,
                'id': rrh['id'],
                'arrival_rate': new_arrival_rate
            })

if __name__ == "__main__":
    generate_parameters()
    generate_topology()
    generate_load()

    now = round(time.time())
    for algorithm in ['normal', 'heuristic', 'optimal']:
        scenario['algorithm'] = algorithm
        scenario['simulation']['KEYWORD'] = '%s-%d' % (algorithm, now)
        scenario['simulation']['CLUSTER_SIZE'] = TARGET_CLUSTERS
        with open('%s/%s.json' % (args.output, scenario['simulation']['KEYWORD']), 'w+') as fout:
            fout.write(json.dumps(scenario, indent = 2))
