from utils.math import next_gaussian
from simulation.sim_parameters import SimulationParams

class Transmission(object):
    def __init__(self, env, source, destination, packet):
        self.env = env

        self.source = source
        self.destination = destination
        self.packet = packet
        self.action = env.process(self.run())

    def get_tx_duration(self):
        if (self.source.type == 'external'):
            mean = float(self.packet.size) * SimulationParams.EXTERNAL_TRANSMISSION_COFACTOR
        else:
            mean = float(self.packet.size) * SimulationParams.INTERNAL_TRANSMISSION_COFACTOR

        return abs(next_gaussian(mean, mean / 10.0))

    def run(self):
        tx_duration = self.get_tx_duration()
        yield self.env.timeout(tx_duration)
        self.destination.put(self.packet)
