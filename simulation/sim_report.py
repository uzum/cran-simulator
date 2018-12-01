import gspread
import time
import os
from oauth2client.service_account import ServiceAccountCredentials
from .sim_parameters import SimulationParams

DRIVE_OWNER = 'a.uzumcuoglu@gmail.com'

class Spreadsheet(object):
    def __init__(self, sheet, create = False):
        # use creds to create a client to interact with the Google Drive API
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(os.path.dirname(__file__), 'credentials.json'), scope)
        client = gspread.authorize(creds)
        if (create == False):
            self.sheet = client.open(sheet)
        else:
            self.sheet = client.create(sheet)

    def append_row(self, values):
        self.sheet.sheet1.append_row(values)

    def share(self):
        self.sheet.share(DRIVE_OWNER, perm_type="user", role="reader", notify=False)

class Report(object):
    def __init__(self, simulation, output):
        self.output = output
        self.simulation = simulation
        self.runs_sheet = Spreadsheet('simulation-times')
        self.steps_sheet = Spreadsheet(output.name, create=True)
        self.start = time.time()

    def print_header(self):
        switch_headers = ''
        for hypervisor in self.simulation.topology.hypervisors:
            switch_headers += 'OVS%dDrop\t' % hypervisor.id
            switch_headers += 'OVS%dUtil.\t' % hypervisor.id

        self.output.write('---- STEP STATS ----\n')
        steps_header = 'Keyword\tTime\tLoad\tReplication\tCost\tWait\tDelay\tDrop\tGain\t%s\n' % switch_headers
        self.output.write(steps_header)
        self.steps_sheet.append_row(steps_header.split('\t'))

    def print_step_report(self):
        switch_stats = ''
        for hypervisor in self.simulation.topology.hypervisors:
            switch_stats += '%f\t' % hypervisor.switch.get_current_drop_rate()
            switch_stats += '%f\t' % self.simulation.topology.get_current_utilization(hypervisor)

        step_result = '%s\t%d\t%d\t%f\t%f\t%f\t%f\t%f\t%f\t%s\n' % (
            SimulationParams.KEYWORD,
            self.simulation.env.now,
            self.simulation.topology.get_current_load(),
            self.simulation.topology.get_current_replication_factor(),
            self.simulation.topology.get_transmission_cost(),
            self.simulation.topology.get_current_wait(),
            self.simulation.topology.get_current_delay(),
            self.simulation.topology.get_current_drop_rate(),
            self.simulation.topology.get_utilization_gain(),
            switch_stats
        )
        self.output.write(step_result)
        self.steps_sheet.append_row(step_result.split('\t'))
        self.output.flush()

    def print_overall_report(self):
        self.output.write('-------RRH STATS--------' + '\n')
        self.output.write('id\tpackets sent\n')
        for rrh in self.simulation.topology.rrhs:
            self.output.write('%d\t%d\n' % (rrh.id, rrh.packets_sent))
        self.output.write('--------------------------\n\n')

        self.output.write('-------BBU STATS----------\n')
        self.output.write('id\tpackets rec.\taverage wait\taverage delay\n')
        for hypervisor in self.simulation.topology.hypervisors:
            for bbu in hypervisor.bbus:
                self.output.write('%d\t%d\t%f\t%f\n' % (bbu.id, bbu.packets_rec, bbu.get_lifetime_wait(), bbu.get_lifetime_delay()))
        self.output.write('overall average wait: %f\n' % self.simulation.topology.get_lifetime_wait())
        self.output.write('overall average delay: %f\n' % self.simulation.topology.get_lifetime_delay())
        self.output.write('--------------------------\n\n')

        self.output.write('-----EXT-SWITCH--------' + '\n')
        self.output.write('packets rec: %d\n' % self.simulation.topology.external_switch.packets_rec)
        self.output.write('packets drop: %d\n' % self.simulation.topology.external_switch.packets_drop)
        self.output.write('drop rate: %f\n' % self.simulation.topology.external_switch.get_lifetime_drop_rate())
        self.output.write('------------------------\n\n')

        self.output.write('-------OVS-SWITCHES-------' + '\n')
        self.output.write('hypervisor id\tpackets rec.\tpackets drop.\tdrop rate\n')
        for hypervisor in self.simulation.topology.hypervisors:
            self.output.write('%d\t%d\t%d\t%f\n' % (hypervisor.id, hypervisor.switch.packets_rec, hypervisor.switch.packets_drop, hypervisor.switch.get_lifetime_drop_rate()))
        self.output.write('\noverall drop rate: %f\n' % self.simulation.topology.get_lifetime_drop_rate())
        self.output.write('-------------------------\n\n')

        simulation_time = time.time() - self.start
        self.output.write('Simulation time: %.2f ms' % simulation_time)

        self.runs_sheet.append_row([
            SimulationParams.KEYWORD,
            self.simulation.configuration['algorithm'],
            len(self.simulation.topology.hypervisors),
            len(self.simulation.topology.rrhs),
            SimulationParams.CLUSTER_SIZE,
            '%.3f' % simulation_time
        ])
        self.steps_sheet.share()
