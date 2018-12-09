from entities.remote_radio_head import RemoteRadioHead
from entities.hypervisor import Hypervisor
from entities.baseband_unit import BasebandUnit
from entities.switch import Switch
from forwarding.forwarding import Forwarding

class StatHistory(object):
    history = {}

    def get(key, current):
        if (key in StatHistory.history):
            value = current - StatHistory.history[key]
            StatHistory.history[key] = current
            return value
        StatHistory.history[key] = current
        return current

class Topology(object):
    def __init__(self, env, configuration):
        self.env = env
        self.forwarding = Forwarding(self.env, self)

        self.rrhs = []
        self.hypervisors = []
        self.external_switch = None

        self.stat_history = {}
        self.total_migrations = 0

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
            raise Exception("Target hypervisor not found with the given id")

        for hypervisor in self.hypervisors:
            subject_bbu = hypervisor.find_baseband_unit(bbu_id)
            if (subject_bbu is not None and hypervisor.id != target_hypervisor.id):
                hypervisor.remove_baseband_unit(subject_bbu)
                target_hypervisor.add_baseband_unit(subject_bbu)
                self.total_migrations += 1

    def get_cluster_load(self, cluster):
        load = 0
        for rrh in self.rrhs:
            mapping = self.forwarding.get_mapping(rrh.id)
            for bbu in cluster.baseband_units:
                if (bbu.id in mapping):
                    load += (rrh.arrival_rate * rrh.packet_mean)
                    # break the loop once we found a single transmission
                    break
        return load

    def get_common_load(self, bbu_x, bbu_y):
        if (bbu_x.id == bbu_y.id): return 0
        load = 0
        for rrh in self.rrhs:
            mapping = self.forwarding.get_mapping(rrh.id)
            if (bbu_x.id in mapping and bbu_y.id in mapping):
                load += (rrh.arrival_rate * rrh.packet_mean)
        return load

    def get_transmission_cost(self):
        return StatHistory.get('transmission_cost', self.forwarding.get_transmission_cost())

    def get_migration_count(self):
        return StatHistory.get('migration_count', self.total_migrations)

    def get_current_load(self):
        total = 0
        for rrh in self.rrhs:
            total += (rrh.arrival_rate * rrh.packet_mean * len(self.forwarding.get_mapping(rrh.id)))
        return total

    def get_lifetime_replication_factor(self):
        total_received = 0
        for hypervisor in self.hypervisors:
            total_received += hypervisor.switch.packets_rec
        return total_received / self.external_switch.packets_rec

    def get_current_replication_factor(self):
        total_received = 0
        for hypervisor in self.hypervisors:
            total_received += StatHistory.get('hypervisor.%d.switch.packets_rec' % hypervisor.id, hypervisor.switch.packets_rec)
        if (total_received == 0): return 0.0
        return total_received / StatHistory.get('extswitch.packets_rec', self.external_switch.packets_rec)

    def get_current_wait(self):
        total = 0
        bbu_count = 0
        for hypervisor in self.hypervisors:
            for bbu in hypervisor.bbus:
                total += bbu.get_current_wait()
                bbu_count += 1
        return total / bbu_count

    def get_lifetime_wait(self):
        total = 0
        bbu_count = 0
        for hypervisor in self.hypervisors:
            for bbu in hypervisor.bbus:
                total += bbu.get_lifetime_wait()
                bbu_count += 1
        return total / bbu_count

    def get_current_delay(self):
        total = 0
        bbu_count = 0
        for hypervisor in self.hypervisors:
            for bbu in hypervisor.bbus:
                total += bbu.get_current_delay()
                bbu_count += 1
        return total / bbu_count

    def get_lifetime_delay(self):
        total = 0
        bbu_count = 0
        for hypervisor in self.hypervisors:
            for bbu in hypervisor.bbus:
                total += bbu.get_lifetime_delay()
                bbu_count += 1
        return total / bbu_count

    def get_lifetime_drop_rate(self):
        total = 0
        total_drop = 0
        for hypervisor in self.hypervisors:
            stats = hypervisor.switch.get_lifetime_stats()
            total += (stats['rec'] + stats['drop'])
            total_drop += stats['drop']

        if (total == 0): return 0.0
        return total_drop / total

    def get_current_drop_rate(self):
        total = 0
        total_drop = 0
        for hypervisor in self.hypervisors:
            stats = hypervisor.switch.get_current_stats()
            total += (stats['rec'] + stats['drop'])
            total_drop += stats['drop']

        if (total == 0): return 0.0
        return total_drop / total

    def get_current_utilization(self, hypervisor):
        load = 0
        for rrh in self.rrhs:
            mapping = self.forwarding.get_mapping(rrh.id)
            for bbu in hypervisor.bbus:
                if (bbu.id in mapping):
                    load += (rrh.arrival_rate * rrh.packet_mean)
                    # break the loop once we found a single transmission
                    break
        return load / hypervisor.switch.rate

    def get_utilization_gain(self):
        stopped_hypervisors = 0
        for hypervisor in self.hypervisors:
            if (len(hypervisor.bbus) == 0):
                stopped_hypervisors += 1
        return stopped_hypervisors / len(self.hypervisors)

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
