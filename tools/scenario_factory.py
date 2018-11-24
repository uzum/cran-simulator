import random
import math
import json
import argparse
from plot import plot

parser = argparse.ArgumentParser()
parser.add_argument('--output')
args = parser.parse_args()

# topology parameters
TARGET_CLUSTERS = 8
TARGET_CLUSTER_SIZE = 6
TARGET_NEIGHBOR_SIZE = 2
TARGET_ARRIVAL_RATE = 20.0
TARGET_PACKET_MEAN = 125
TARGET_PACKET_DEV = 20
HYPERVISORS = 5

# simulation parameters
SIMULATION_TIME = 500
STEP_TIME = 5
VIRTUAL_SWITCH_RATE = 50000
VIRTUAL_SWITCH_QLIMIT = 1000
EXTERNAL_TRANSMISSION_COST = 5
INTERNAL_TRANSMISSION_COST = 1
EXTERNAL_TRANSMISSION_COFACTOR = 0.0001
INTERNAL_TRANSMISSION_COFACTOR = 0.0001

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

def generate_topology():
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
            while (len(rrh['baseband_units']) < neighbor_size):
                candidate = random.choice(indexes)
                if (candidate != rrh['id'] and candidate not in rrh['baseband_units']):
                    rrh['baseband_units'].append(candidate)
                random.shuffle(indexes)
            # append its serving station with the same id
            rrh['baseband_units'].append(rrh['id'])
        clusters.append(cluster)

    bbu_per_hypervisor = math.ceil(rrh_id / HYPERVISORS)
    current_hypervisor = scenario['topology']['hypervisors'][0]
    for cluster in clusters:
        for rrh in cluster:
            scenario['topology']['remote_radio_heads'].append(rrh)
            current_hypervisor['baseband_units'].append({ 'id': rrh['id'] })
            if (len(current_hypervisor['baseband_units']) == bbu_per_hypervisor):
                current_hypervisor = { 'id': current_hypervisor['id'] + 1, 'baseband_units': [] }
                scenario['topology']['hypervisors'].append(current_hypervisor)

    # plot(topology, 'test.png')

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

    for algorithm in ['normal', 'heuristic']:
        scenario['algorithm'] = algorithm
        scenario['simulation']['KEYWORD'] = algorithm
        with open('%s/%s.json' % (args.output, algorithm), 'w+') as fout:
            fout.write(json.dumps(scenario, indent = 2))
