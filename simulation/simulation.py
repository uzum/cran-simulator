import simpy
from .topology import Topology
from .algorithm import Algorithm
from .sim_parameters import SimulationParams
from .sim_report import Report

class Simulation(object):
    def __init__(self, configuration, output):
        self.configuration = configuration
        self.env = simpy.Environment()
        for key in configuration['simulation']:
            setattr(SimulationParams, key, configuration['simulation'][key])

        self.topology = Topology(self.env, configuration['topology'])
        self.report = Report(self, output)

    def run(self):
        if (SimulationParams.STEP_TIME == 0):
            self.env.run(until=SimulationParams.SIMULATION_TIME)
        else:
            current = 0
            self.report.print_header()
            while(current < SimulationParams.SIMULATION_TIME):
                current += SimulationParams.STEP_TIME
                if ('updates' in self.configuration):
                    self.process_updates()
                if ('algorithm' in self.configuration):
                    self.process_algorithm(self.configuration['algorithm'])

                self.env.run(until = current)
                self.report.print_step_report()
        self.report.print_overall_report()

    def process_algorithm(self, algorithm):
        assignment = Algorithm.get_assignment(self.topology, algorithm)
        if (len(assignment['residuals']) != 0):
            raise Exception("Failed to allocate all the baseband units into hypervisors")

        for bin in assignment['bins']:
            for element in bin.elements:
                for baseband_unit in element.cluster.baseband_units:
                    self.topology.migrate(baseband_unit.id, bin.hypervisor.id)

    def process_updates(self):
        for key in self.configuration['updates']:
            if (key == 'load'):
                for entry in self.configuration['updates']['load']:
                    if (entry['time'] == self.env.now):
                        self.topology.update_load(entry['id'], entry['arrival_rate'])
            elif (key == 'migration'):
                for entry in self.configuration['updates']['migration']:
                    if (entry['time'] == self.env.now):
                        self.topology.migrate(entry['id'], entry['hypervisor'])

    def report(self):
        self.report.print_overall_report()
