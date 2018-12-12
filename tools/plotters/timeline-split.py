import matplotlib.pyplot as plt
import numpy as np
import csv

markers = {
    'kargers': { 'timestamps': [], 'repl': [], 'repl_err': [], 'cost': [], 'cost_err': [], 'migr': [], 'migr_err': [], 'drop': [], 'drop_err': [], 'effc': [], 'effc_err': [] },
    'random': { 'timestamps': [], 'repl': [], 'repl_err': [], 'cost': [], 'cost_err': [], 'migr': [], 'migr_err': [], 'drop': [], 'drop_err': [], 'effc': [], 'effc_err': [] }
}

color_map = {
    'kargers': 'r',
    'random': 'm'
}

for algorithm in ['random', 'kargers']:
    with open('./timeline-%s.csv' % algorithm, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter="\t")
        for row in reader:
            markers[algorithm]['timestamps'].append(float(row[1].replace(',', '')))
            markers[algorithm]['repl'].append(float(row[2].replace(',', '')))
            markers[algorithm]['cost'].append(float(row[3].replace(',', '')))
            markers[algorithm]['migr'].append(float(row[4].replace(',', '')))
            markers[algorithm]['drop'].append(float(row[7].replace(',', '')))
            markers[algorithm]['effc'].append(float(row[8].replace(',', '')))
            markers[algorithm]['repl_err'].append(float(row[9].replace(',', '')) - float(row[2].replace(',', '')))
            markers[algorithm]['cost_err'].append(float(row[11].replace(',', '')) - float(row[3].replace(',', '')))
            markers[algorithm]['migr_err'].append(float(row[13].replace(',', '')) - float(row[4].replace(',', '')))
            markers[algorithm]['drop_err'].append(float(row[15].replace(',', '')) - float(row[7].replace(',', '')))
            markers[algorithm]['effc_err'].append(float(row[17].replace(',', '')) - float(row[8].replace(',', '')))

fig, axs = plt.subplots(nrows=4, ncols=1, figsize=(12, 27))
for algorithm in ['random', 'kargers']:
    axs[0].errorbar(markers[algorithm]['timestamps'], markers[algorithm]['repl'], yerr=markers[algorithm]['repl_err'], fmt='o', capsize=3, color = color_map[algorithm], alpha=0.7, label=algorithm)
    axs[1].errorbar(markers[algorithm]['timestamps'], markers[algorithm]['cost'], yerr=markers[algorithm]['cost_err'], fmt='o', capsize=3, color = color_map[algorithm], alpha=0.7, label=algorithm)
    axs[2].errorbar(markers[algorithm]['timestamps'], markers[algorithm]['effc'], yerr=markers[algorithm]['effc_err'], fmt='o', capsize=3, color = color_map[algorithm], alpha=0.7, label=algorithm)
    axs[3].errorbar(markers[algorithm]['timestamps'], markers[algorithm]['migr'], yerr=markers[algorithm]['migr_err'], fmt='o', capsize=3, color = color_map[algorithm], alpha=0.7, label=algorithm)

axs[0].set_xlabel('Time')
axs[0].set_ylabel('Replication factor')
axs[0].legend()
axs[1].set_xlabel('Time')
axs[1].set_ylabel('Cost value')
axs[1].legend()
axs[2].set_xlabel('Time')
axs[2].set_ylabel('Energy efficiency')
axs[2].legend()
axs[3].set_xlabel('Time')
axs[3].set_ylabel('Migration count')
axs[3].legend()


plt.tight_layout()
plt.grid()
plt.savefig('timeline-split.png')
