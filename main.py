import argparse
import json
from os import listdir
from simulation.simulation import Simulation

parser = argparse.ArgumentParser()
parser.add_argument('--config')
parser.add_argument('--folder')
args = parser.parse_args()

if (args.config):
    with open(args.config) as f:
        configuration = json.load(f)

        with open(args.config + '.out', 'w+') as fout:
            sim = Simulation(configuration, fout)
            sim.run()
            sim.report()

elif (args.folder):
    for conf_file in listdir(args.folder):
        if (conf_file.endswith('json')):
            with open(args.folder + '/' + conf_file) as f:
                configuration = json.load(f)

                with open(args.folder + '/' + conf_file + '.out', 'w+') as fout:
                    sim = Simulation(configuration, fout)
                    sim.run()
                    sim.report()
                    print('completed %s' % conf_file)
