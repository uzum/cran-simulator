import argparse
import json
from simulation.simulation import Simulation

parser = argparse.ArgumentParser()
parser.add_argument('config')
args = parser.parse_args()

with open(args.config) as f:
    configuration = json.load(f)

sim = Simulation(configuration)
sim.run()
sim.report()
