import simpy
from .topology import Topology
from .sim_parameters import SimulationParams

class Simulation(object):
    def __init__(self, configuration, output):
        self.configuration = configuration
        self.env = simpy.Environment()
        self.output = output
        for key in configuration['simulation']:
            setattr(SimulationParams, key, configuration['simulation'][key])

        self.topology = Topology(self.env, configuration['topology'])

    def run(self):
        if (SimulationParams.STEP_TIME == 0):
            self.env.run(until=SimulationParams.SIMULATION_TIME)
        else:
            current = 0
            self.output.write('------ STEP STATS ------\n')
            self.output.write('Time\tLoad\tWait\tDelay\tDrop\n')
            while(current < SimulationParams.SIMULATION_TIME):
                current += SimulationParams.STEP_TIME
                if ('updates' in self.configuration):
                    self.process_updates()
                self.env.run(until = current)
                self.step_report()

    def process_updates(self):
        for key in self.configuration['updates']:
            if (key == 'load'):
                for entry in self.configuration['updates']['load']:
                    if (entry['time'] == self.env.now):
                        self.topology.update_load(entry)

    def step_report(self):
        self.output.write('%d\t%d\t%f\t%f\t%f\n' % (
            self.env.now,
            self.topology.get_current_load(),
            self.topology.get_overall_wait(),
            self.topology.get_overall_delay(),
            self.topology.get_overall_drop_rate()
        ))
        self.output.flush()

    def report(self):
        self.output.write('-------RRH STATS--------' + '\n')
        self.output.write('id\tpackets sent\n')
        for rrh in self.topology.rrhs:
            self.output.write('%d\t%d\n' % (rrh.id, rrh.packets_sent))
        self.output.write('--------------------------\n\n')

        self.output.write('-------BBU STATS----------\n')
        self.output.write('id\tpackets rec.\taverage wait\taverage delay\n')
        for hypervisor in self.topology.hypervisors:
            for bbu in hypervisor.bbus:
                self.output.write('%d\t%d\t%f\t%f\n' % (bbu.id, bbu.packets_rec, self.topology.get_average_wait(bbu), self.topology.get_average_delay(bbu)))
        self.output.write('overall average wait: %f\n' % self.topology.get_overall_wait())
        self.output.write('overall average delay: %f\n' % self.topology.get_overall_delay())
        self.output.write('--------------------------\n\n')

        self.output.write('-----EXT-SWITCH--------' + '\n')
        self.output.write('packets rec: %d\n' % self.topology.external_switch.packets_rec)
        self.output.write('packets drop: %d\n' % self.topology.external_switch.packets_drop)
        self.output.write('drop rate: %f\n' % self.topology.get_drop_rate(self.topology.external_switch))
        self.output.write('------------------------\n\n')

        self.output.write('-------OVS-SWITCHES-------' + '\n')
        self.output.write('hypervisor id\tpackets rec.\tpackets drop.\tdrop rate\n')
        for hypervisor in self.topology.hypervisors:
            self.output.write('%d\t%d\t%d\t%f\n' % (hypervisor.id, hypervisor.switch.packets_rec, hypervisor.switch.packets_drop, self.topology.get_drop_rate(hypervisor.switch)))
        self.output.write('\noverall drop rate: %f\n' % self.topology.get_overall_drop_rate())
        self.output.write('-------------------------\n\n')
