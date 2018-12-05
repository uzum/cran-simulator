import csv
import numpy as np
import matplotlib.pyplot as plt

markers = {
    'heuristic': { 'x': [], 'y': [] },
    'optimal': { 'x': [], 'y': [] },
    'normal': { 'x': [], 'y': [] }
}

with open('./time-data.csv', 'r') as csvfile:
    reader = csv.reader(csvfile, delimiter="\t")
    for row in reader:
        markers[row[0]]['x'].append(float(row[2]))
        markers[row[0]]['y'].append(float(row[4].replace(',', '')))

plt.figure(figsize=(20, 10))
plt.scatter(markers['heuristic']['x'], markers['heuristic']['y'], color = 'r', alpha=0.5, label="heuristic")
plt.scatter(markers['normal']['x'], markers['normal']['y'], color = 'm', alpha=0.5, label="normal")
plt.scatter(markers['optimal']['x'], markers['optimal']['y'], color = 'c', alpha=0.5, label="optimal")
plt.grid()
plt.legend()
plt.xlabel('Number of RRHs')
plt.ylabel('Simulation time (s)')
plt.savefig('scatter.png')
