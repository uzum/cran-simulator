import matplotlib.pyplot as plt
import numpy as np
import csv

markers = {
    'heuristic': { 'timestamps': [], 'repl': [], 'cost': [], 'migr': [], 'drop': [], 'effc': [] },
    'optimal': { 'timestamps': [], 'repl': [], 'cost': [], 'migr': [], 'drop': [], 'effc': [] },
    'normal': { 'timestamps': [], 'repl': [], 'cost': [], 'migr': [], 'drop': [], 'effc': [] }
}

color_map = {
    'heuristic': 'r',
    'normal': 'm',
    'optimal': 'c'
}

for algorithm in ['optimal', 'heuristic', 'normal']:
    for i in range(0, 5):
        with open('./data/timeline-%s-%d.csv' % (algorithm, i), 'r') as csvfile:
            reader = csv.reader(csvfile, delimiter="\t")
            for row in reader:
                markers[algorithm]['timestamps'].append(float(row[1].replace(',', '')))
                markers[algorithm]['repl'].append(float(row[3].replace(',', '')))
                markers[algorithm]['cost'].append(float(row[4].replace(',', '')))
                markers[algorithm]['migr'].append(float(row[5].replace(',', '')))
                markers[algorithm]['drop'].append(float(row[8].replace(',', '')))
                markers[algorithm]['effc'].append(float(row[9].replace(',', '')))

fig, axs = plt.subplots(nrows=5, ncols=1, figsize=(12, 30))
for algorithm in ['optimal', 'heuristic', 'normal']:
    axs[0].scatter(markers[algorithm]['timestamps'], markers[algorithm]['repl'], color = color_map[algorithm], alpha=0.7, label=algorithm)
    axs[1].scatter(markers[algorithm]['timestamps'], markers[algorithm]['cost'], color = color_map[algorithm], alpha=0.7, label=algorithm)
    axs[2].scatter(markers[algorithm]['timestamps'], markers[algorithm]['drop'], color = color_map[algorithm], alpha=0.7, label=algorithm)
    axs[3].scatter(markers[algorithm]['timestamps'], markers[algorithm]['effc'], color = color_map[algorithm], alpha=0.7, label=algorithm)
    axs[4].scatter(markers[algorithm]['timestamps'], markers[algorithm]['migr'], color = color_map[algorithm], alpha=0.7, label=algorithm)

axs[0].set_xlabel('Time')
axs[0].set_ylabel('Replication factor')
axs[0].legend()
axs[1].set_xlabel('Time')
axs[1].set_ylabel('Cost value')
axs[1].legend()
axs[2].set_xlabel('Time')
axs[2].set_ylabel('Drop rate')
axs[2].legend()
axs[3].set_xlabel('Time')
axs[3].set_ylabel('Energy efficiency')
axs[3].legend()
axs[4].set_xlabel('Time')
axs[4].set_ylabel('Migration count')
axs[4].legend()

plt.tight_layout()
plt.grid()
plt.savefig('timeline.png')
