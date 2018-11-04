import simpy

class Switch(object):
    def __init__(self, env, host, type, rate=20000.0, qlimit=None, limit_bytes=True, debug=False):
        self.store = simpy.Store(env)
        self.host = host
        self.type = type
        self.rate = rate
        self.env = env
        self.outs = []
        self.packets_rec = 0
        self.packets_drop = 0
        self.qlimit = qlimit
        self.limit_bytes = limit_bytes
        self.byte_size = 0  # Current size of the queue in bytes
        self.debug = debug
        self.busy = 0  # Used to track if a packet is currently being sent
        self.action = env.process(self.run())  # starts the run() method as a SimPy process
        self.forwarding_function = None

    def set_forwarding_function(self, function):
        self.forwarding_function = function

    def send_packet(self, packet):
        self.forwarding_function(self, packet)

    def add_port(self, out):
        self.outs.append(out);

    def run(self):
        while True:
            packet = (yield self.store.get())
            self.busy = 1
            self.byte_size -= packet.size
            yield self.env.timeout(packet.size*8.0/self.rate)
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
