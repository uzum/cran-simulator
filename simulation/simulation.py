import simpy
from .topology import Topology
from .sim_parameters import SimulationParams

class Simulation(object):
    def __init__(self, configuration):
        self.configuration = configuration
        self.env = simpy.Environment()
        for key in configuration['simulation']:
            setattr(SimulationParams, key, configuration['simulation'][key])

        self.topology = Topology(self.env, configuration['topology'])

    def run(self):
        self.env.run()

    def report(self):
        print('-------BBU STATS----------')
        for hypervisor in self.topology.hypervisors:
            for bbu in hypervisor.bbus:
                print('bbu id: %d' % bbu.id)
                print('packets rec: %d' % bbu.packets_rec)
                if (len(bbu.waits) > 0): print('average wait: %f' % (sum(bbu.waits) / float(len(bbu.waits))))
                if (len(bbu.arrivals) > 0): print('average arrival: %f' % (sum(bbu.arrivals) / float(len(bbu.arrivals))))
                print('\n')
        print('--------------------------\n\n')

        print('-------OVS-SWITCHES-------')
        for hypervisor in self.topology.hypervisors:
            print('switch in hypervisor: %d' % hypervisor.id)
            print('packets rec: %d' % hypervisor.switch.packets_rec)
            print('packets drop: %d' % hypervisor.switch.packets_drop)
        print('-------------------------\n\n')

        print('-----EXT-SWITCH--------')
        print('packets rec: %d' % self.topology.external_switch.packets_rec)
        print('packets drop: %d' % self.topology.external_switch.packets_drop)
        print('------------------------\n\n')

        print('-------RRH STATS--------')
        for rrh in self.topology.rrhs:
            print('rrh id: %d' % rrh.id)
            print('packets sent: %d' % rrh.packets_sent)
