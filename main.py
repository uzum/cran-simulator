import simpy
from random import expovariate

from topology import Topology
env = simpy.Environment()
topo = Topology(env)

env.run(until=100)
