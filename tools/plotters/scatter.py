import numpy as np
import matplotlib.pyplot as plt
import json

with open("./data.json") as f:
    data = json.load(f)

markers = {
    'heuristic': { 'x': [], 'y': [] },
    'optimal': { 'x': [], 'y': [] },
    'normal': { 'x': [], 'y': [] }
}

for run in data['array']:
    markers[run[0]]['x'].append(run[2])
    markers[run[0]]['y'].append(run[4])

plt.scatter(markers['heuristic']['x'], markers['heuristic']['y'], color = 'r', alpha=0.5)
plt.scatter(markers['optimal']['x'], markers['optimal']['y'], color = 'c', alpha=0.5)
plt.scatter(markers['normal']['x'], markers['normal']['y'], color = 'm', alpha=0.5)
plt.savefig('demo.png')
