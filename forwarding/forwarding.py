import copy
from .transmission import Transmission

def find(list, fn):
    for item in list:
        if fn(item):
            return item
    return None

class Mapping(object):
    def __init__(self, remote_radio_head, baseband_units):
        self.remote_radio_head = remote_radio_head
        self.baseband_units = baseband_units

class Forwarding(object):
    def __init__(self, env, topology):
        self.env = env
        self.mappings = []
        self.topology = topology
        self.transmission_cost = 0

    def add_mapping(self, remote_radio_head, baseband_units):
        self.mappings.append(Mapping(remote_radio_head, baseband_units))

    def get_mapping(self, remote_radio_head):
        for mapping in self.mappings:
            if mapping.remote_radio_head == remote_radio_head:
                return mapping.baseband_units

    def get_transmission_cost(self):
        return self.transmission_cost

    def reset_transmission_cost(self):
        self.transmission_cost = 0

    def forwarding_function(self, switch, packet):
        mapping = find(self.mappings, lambda m: m.remote_radio_head == packet.src)
        if (mapping == None):
            raise AttributeError('No mapping is defined for rrh id#%d' % packet.src)

        if (switch.type == 'external'):
            forwardedOnce = False
            for hypervisor in self.topology.hypervisors:
                for bbu in hypervisor.bbus:
                    if bbu.id in mapping.baseband_units:
                        # introduce external to internal delay:
                        if (forwardedOnce):
                            packet_clone = copy.copy(packet)
                            self.transmission_cost += Transmission(self.env, switch, hypervisor.switch, packet_clone).get_tx_cost()
                        else:
                            self.transmission_cost += Transmission(self.env, switch, hypervisor.switch, packet).get_tx_cost()
                            # we have forwarded the packet once, further deduplication will be made in internal switch
                            forwardedOnce = True
                            break

        elif (switch.type == 'internal'):
            hypervisor = find(self.topology.hypervisors, lambda hypervisor: hypervisor.id == switch.host)
            forwardedOnce = False
            for out in hypervisor.switch.outs:
                if out.id in mapping.baseband_units:
                    if (forwardedOnce):
                        packet_clone = copy.copy(packet)
                        self.transmission_cost += Transmission(self.env, switch, out, packet_clone).get_tx_cost()
                    else:
                        self.transmission_cost += Transmission(self.env, switch, out, packet).get_tx_cost()
                        forwardedOnce = True
