from entities.remote_radio_head import RemoteRadioHead
from entities.hypervisor import Hypervisor
from entities.baseband_unit import BasebandUnit
from entities.switch import Switch
from forwarding.forwarding import Forwarding

class Topology(object):
    def __init__(self, env, configuration):
        self.env = env
        self.forwarding = Forwarding(self.env, self)

        self.rrhs = []
        self.hypervisors = []
        self.external_switch = None

        self.setup(configuration)

    def update_load(self, rrh_id, arrival_rate = None, packet_mean = None, packet_dev = None):
        for rrh in self.rrhs:
            if (rrh.id == rrh_id):
                if arrival_rate is not None:
                    rrh.set_arrival_rate(arrival_rate)
                if packet_mean is not None:
                    rrh.set_packet_mean(packet_mean)
                if packet_dev is not None:
                    rrh.set_packet_dev(packet_dev)

    def migrate(self, bbu_id, target_hypervisor_id):
        target_hypervisor = [hv for hv in self.hypervisors if hv.id == target_hypervisor_id][0]
        if (target_hypervisor is None):
            raise "Target hypervisor not found with the given id"

        for hypervisor in self.hypervisors:
            subject_bbu = hypervisor.find_baseband_unit(bbu_id)
            if (subject_bbu is not None):
                hypervisor.remove_baseband_unit(subject_bbu)
                target_hypervisor.add_baseband_unit(subject_bbu)

    def get_transmission_cost(self):
        cost = self.forwarding.get_transmission_cost()
        self.forwarding.reset_transmission_cost()
        return cost

    def get_current_load(self):
        total = 0
        for rrh in self.rrhs:
            total += (rrh.arrival_rate * rrh.packet_mean * len(self.forwarding.get_mapping(rrh.id)))
        return total

    def get_replication_factor(self):
        total_received = 0
        for hypervisor in self.hypervisors:
            total_received += hypervisor.switch.packets_rec
        return total_received / self.external_switch.packets_rec

    def get_average_delay(self, baseband_unit):
        if (len(baseband_unit.arrivals) == 0): return 0.0
        return sum(baseband_unit.arrivals) / len(baseband_unit.arrivals)

    def get_average_wait(self, baseband_unit):
        if (len(baseband_unit.waits) == 0): return 0.0
        return sum(baseband_unit.waits) / len(baseband_unit.waits)

    def get_overall_delay(self):
        total = 0
        bbu_count = 0
        for hypervisor in self.hypervisors:
            for bbu in hypervisor.bbus:
                total += self.get_average_delay(bbu)
                bbu_count += 1
        return total / bbu_count

    def get_overall_wait(self):
        total = 0
        bbu_count = 0
        for hypervisor in self.hypervisors:
            for bbu in hypervisor.bbus:
                total += self.get_average_wait(bbu)
                bbu_count += 1
        return total / bbu_count

    def get_drop_rate(self, switch):
        total = switch.packets_drop + switch.packets_rec
        return switch.packets_drop / total

    def get_overall_drop_rate(self):
        total = 0
        total_drop = 0
        for hypervisor in self.hypervisors:
            total += (hypervisor.switch.packets_rec + hypervisor.switch.packets_drop)
            total_drop += hypervisor.switch.packets_drop
        return total_drop / total

    def setup(self, configuration):
        self.external_switch = Switch(self.env, 'physical', 'external')
        self.external_switch.set_forwarding_function(self.forwarding.forwarding_function)

        for remote_radio_head in configuration['remote_radio_heads']:
            rrh_object = RemoteRadioHead(self.env, remote_radio_head['id'])
            rrh_object.set_arrival_rate(remote_radio_head['arrival_rate'])
            rrh_object.set_packet_mean(remote_radio_head['packet_mean'])
            rrh_object.set_packet_dev(remote_radio_head['packet_dev'])
            rrh_object.out = self.external_switch
            self.rrhs.append(rrh_object)
            self.forwarding.add_mapping(remote_radio_head['id'], remote_radio_head['baseband_units'])

        for hypervisor in configuration['hypervisors']:
            hypervisor_object = Hypervisor(self.env, hypervisor['id'])
            for baseband_unit in hypervisor['baseband_units']:
                bbu_object = BasebandUnit(self.env, baseband_unit['id'])
                hypervisor_object.add_baseband_unit(bbu_object)
            hypervisor_object.switch.set_forwarding_function(self.forwarding.forwarding_function)
            self.hypervisors.append(hypervisor_object)
