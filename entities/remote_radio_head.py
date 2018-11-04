from .udp_packet import UDPPacket
import numpy
import math
import random

DEFAULT_ARRIVAL_RATE = 30.0
DEFAULT_PACKET_MEAN = 100
DEFAULT_PACKET_DEV = 20

class RemoteRadioHead(object):
    def __init__(self, env, id, initial_delay=0, finish=float("inf")):
        self.id = id
        self.env = env
        self.initial_delay = initial_delay
        self.finish = finish
        self.out = None
        self.packets_sent = 0
        self.action = env.process(self.run())
        self.arrival_rate = DEFAULT_ARRIVAL_RATE
        self.packet_mean = DEFAULT_PACKET_MEAN
        self.packet_dev = DEFAULT_PACKET_DEV

    def next_poisson(self):
        return -math.log(1.0 - random.random()) / self.arrival_rate

    def next_gaussian(self):
        return int(numpy.random.normal(self.packet_mean, self.packet_dev, 1))

    def run(self):
        yield self.env.timeout(self.initial_delay)
        while self.env.now < self.finish:
            yield self.env.timeout(self.next_poisson())
            self.packets_sent += 1
            print('sending packet from rrh#%d', self.id)
            self.out.put(UDPPacket(self.env.now, self.next_gaussian(), self.packets_sent, src = self.id))
