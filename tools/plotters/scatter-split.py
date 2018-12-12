import csv
import numpy as np
import matplotlib.pyplot as plt

markers = {
    'kargers': {
        'rrh': [],
        'repl': [],
        'drop': []
    },
    'random': {
        'rrh': [],
        'repl': [],
        'drop': []
    }
}

color_map = {
    'kargers': 'r',
    'random': 'm'
}

with open('./split-data.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter="\t")
    for row in reader:
        handle = None
        if (row[0] == 'r'):
            handle = markers['random']
        else:
            handle = markers['kargers']

        handle['rrh'].append(int(row[1].replace(',', '')))
        handle['repl'].append(float(row[2].replace(',', '')))
        handle['drop'].append(float(row[3].replace(',', '')))

fig, axs = plt.subplots(nrows=2, ncols=1, figsize=(12, 12))
for algorithm in ['kargers', 'random']:
    axs[0].scatter(markers[algorithm]['rrh'], markers[algorithm]['repl'], color = color_map[algorithm], alpha=0.7, label=algorithm)
    axs[1].scatter(markers[algorithm]['rrh'], markers[algorithm]['drop'], color = color_map[algorithm], alpha=0.7, label=algorithm)

axs[0].set_xlabel('RRH Number')
axs[0].set_ylabel('Replication factor')
axs[0].legend()
axs[1].set_xlabel('RRH Number')
axs[1].set_ylabel('Drop rate')
axs[1].legend()


plt.tight_layout()
plt.grid()
plt.savefig('scatter-split.png')
