from .udp_packet import UDPPacket
from utils.math import next_poisson, next_gaussian
from simulation.sim_parameters import SimulationParams

DEFAULT_ARRIVAL_RATE = 30.0
DEFAULT_PACKET_MEAN = 100
DEFAULT_PACKET_DEV = 20

class RemoteRadioHead(object):
    def __init__(self, env, id):
        self.id = id
        self.env = env
        self.initial_delay = SimulationParams.PACKET_GENERATION_DELAY
        self.finish = SimulationParams.PACKET_GENERATION_FINISH
        self.out = None
        self.packets_sent = 0
        self.action = env.process(self.run())
        self.arrival_rate = DEFAULT_ARRIVAL_RATE
        self.packet_mean = DEFAULT_PACKET_MEAN
        self.packet_dev = DEFAULT_PACKET_DEV

    def set_arrival_rate(self, rate):
        self.arrival_rate = rate

    def set_packet_mean(self, mean):
        self.packet_mean = mean

    def set_packet_dev(self, dev):
        self.packet_dev = dev

    def run(self):
        yield self.env.timeout(self.initial_delay)
        while self.env.now < self.finish:
            yield self.env.timeout(next_poisson(self.arrival_rate))
            self.packets_sent += 1
            self.out.put(UDPPacket(self.env.now, next_gaussian(self.packet_mean, self.packet_dev), self.packets_sent, src = self.id))
