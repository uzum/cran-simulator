import simpy
from simulation.sim_parameters import SimulationParams

class Switch(object):
    def __init__(self, env, host, type, rate=float('inf'), qlimit=None, limit_bytes=True, debug=False):
        self.store = simpy.Store(env)
        self.host = host
        self.type = type
        self.rate = rate
        if (type == 'internal'):
            self.rate = SimulationParams.VIRTUAL_SWITCH_RATE
        self.qlimit = SimulationParams.VIRTUAL_SWITCH_QLIMIT
        self.env = env
        self.outs = []
        self.packets_rec = 0
        self.packets_drop = 0
        self.limit_bytes = limit_bytes
        self.byte_size = 0  # Current size of the queue in bytes
        self.debug = debug
        self.busy = 0  # Used to track if a packet is currently being sent
        self.action = env.process(self.run())  # starts the run() method as a SimPy process
        self.forwarding_function = None
        self.last_peek_packets_rec = 0
        self.last_peek_packets_drop = 0

    def set_forwarding_function(self, function):
        self.forwarding_function = function

    def send_packet(self, packet):
        self.forwarding_function(self, packet)

    def add_port(self, out):
        self.outs.append(out)

    def remove_port(self, out):
        self.outs.remove(out)

    def peek_current_stats(self):
        interval_rec = self.packets_rec - self.last_peek_packets_rec
        interval_drop = self.packets_drop - self.last_peek_packets_drop
        return { 'rec': interval_rec, 'drop': interval_drop }

    def get_current_stats(self):
        stats = self.peek_current_stats()
        self.last_peek_packets_rec = self.packets_rec
        self.last_peek_packets_drop = self.packets_drop
        return stats

    def get_lifetime_stats(self):
        return { 'rec': self.packets_rec, 'drop': self.packets_drop }

    def get_current_drop_rate(self):
        stats = self.peek_current_stats()
        if (stats['rec'] + stats['drop'] == 0): return 0.0
        return stats['drop'] / (stats['drop'] + stats['rec'])

    def get_lifetime_drop_rate(self):
        if (self.packets_rec + self.packets_drop == 0): return 0.0
        return self.packets_drop / (self.packets_rec + self.packets_drop)

    def run(self):
        while True:
            packet = (yield self.store.get())
            self.busy = 1
            self.byte_size -= packet.size
            yield self.env.timeout(packet.size/self.rate)
            self.send_packet(packet)
            self.busy = 0
            if self.debug:
                print(packet)

    def put(self, pkt):
        self.packets_rec += 1
        tmp_byte_count = self.byte_size + pkt.size

        if self.qlimit is None:
            self.byte_size = tmp_byte_count
            return self.store.put(pkt)
        if self.limit_bytes and tmp_byte_count >= self.qlimit:
            self.packets_drop += 1
            return
        elif not self.limit_bytes and len(self.store.items) >= self.qlimit-1:
            self.packets_drop += 1
        else:
            self.byte_size = tmp_byte_count
            return self.store.put(pkt)
