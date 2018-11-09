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
        self.env.run(until=SimulationParams.SIMULATION_TIME)

    def report(self, file):
        file.write('-------RRH STATS--------' + '\n')
        file.write('id\tpackets sent\n')
        for rrh in self.topology.rrhs:
            file.write('%d\t%d\n' % (rrh.id, rrh.packets_sent))
        file.write('--------------------------\n\n')

        file.write('-------BBU STATS----------\n')
        file.write('id\tpackets rec.\taverage wait\taverage delay\n')
        for hypervisor in self.topology.hypervisors:
            for bbu in hypervisor.bbus:
                file.write('%d\t%d\t%f\t%f\n' % (bbu.id, bbu.packets_rec, (sum(bbu.waits) / float(len(bbu.waits))), (sum(bbu.arrivals) / float(len(bbu.arrivals)))))
        file.write('--------------------------\n\n')


        file.write('-----EXT-SWITCH--------' + '\n')
        file.write('packets rec: %d\n' % self.topology.external_switch.packets_rec)
        file.write('packets drop: %d\n' % self.topology.external_switch.packets_drop)
        total = self.topology.external_switch.packets_rec + self.topology.external_switch.packets_drop
        drop_rate = self.topology.external_switch.packets_drop / total
        file.write('packets total: %d\n' % total)
        file.write('drop rate: %f\n' % drop_rate)
        file.write('------------------------\n\n')

        file.write('-------OVS-SWITCHES-------' + '\n')
        file.write('hypervisor id\tpackets rec.\tpackets drop.\tdrop rate\n')
        total_received = 0
        total_dropped = 0
        for hypervisor in self.topology.hypervisors:
            total = hypervisor.switch.packets_rec + hypervisor.switch.packets_drop
            drop_rate = hypervisor.switch.packets_drop / total
            file.write('%d\t%d\t%d\t%f\n' % (hypervisor.id, hypervisor.switch.packets_rec, hypervisor.switch.packets_drop, drop_rate))
            total_received += hypervisor.switch.packets_rec
            total_dropped += hypervisor.switch.packets_drop
        drop_rate = total_dropped / (total_received + total_dropped)
        file.write('\noverall drop rate: %f\n' % drop_rate)
        file.write('-------------------------\n\n')
