import simpy
from simulation.sim_parameters import SimulationParams

class BasebandUnit(object):
    def __init__(self, env, id, rec_arrivals=True, absolute_arrivals=False, rec_waits=True, selector=None):
        self.store = simpy.Store(env)
        self.env = env
        self.id = id
        self.rec_waits = rec_waits
        self.rec_arrivals = rec_arrivals
        self.absolute_arrivals = absolute_arrivals
        self.waits = []
        self.arrivals = []
        self.debug = SimulationParams.BBU_DEBUG
        self.packets_rec = 0
        self.bytes_rec = 0
        self.selector = selector
        self.last_arrival = 0.0

    def put(self, pkt):
        if not self.selector or self.selector(pkt):
            now = self.env.now
            if self.rec_waits:
                self.waits.append(self.env.now - pkt.time)
            if self.rec_arrivals:
                if self.absolute_arrivals:
                    self.arrivals.append(now)
                else:
                    self.arrivals.append(now - self.last_arrival)
                self.last_arrival = now
            self.packets_rec += 1
            self.bytes_rec += pkt.size
            if self.debug:
                print('bbu#%d | %s' % (self.id, pkt))

    def __repr__(self):
        return "BBU#%d" % self.id
