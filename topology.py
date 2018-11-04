from entities.remote_radio_head import RemoteRadioHead
from entities.hypervisor import Hypervisor
from entities.baseband_unit import BasebandUnit
from entities.switch import Switch
from forwarding import forwarding_function

class Mapping(object):
    def __init__(self, remote_radio_head, baseband_units):
        self.remote_radio_head = remote_radio_head
        self.baseband_units = baseband_units

class Topology(object):
    def __init__(self, env):
        self.env = env
        self.mappings = []
        self.rrhs = []
        self.hypervisors = []
        self.setup()

    def forwarding_function(self, switch, packet):
        forwarding_function(self, switch, packet)

    def setup(self):
        self.rrhs = [
            RemoteRadioHead(self.env, 0),
            RemoteRadioHead(self.env, 1)
        ]
        self.hypervisors = [
            Hypervisor(self.env, 2)
        ]
        self.hypervisors[0].add_baseband_unit(BasebandUnit(self.env, 3, debug=True))
        self.hypervisors[0].add_baseband_unit(BasebandUnit(self.env, 4, debug=True))
        self.hypervisors[0].switch.set_forwarding_function(self.forwarding_function)
        self.external_switch = Switch(self.env, 'physical', 'external')
        self.external_switch.set_forwarding_function(self.forwarding_function)

        self.rrhs[0].out = self.external_switch
        self.rrhs[1].out = self.external_switch
        self.set_mapping(self.rrhs[0], [self.hypervisors[0].bbus[0]])
        self.set_mapping(self.rrhs[1], [self.hypervisors[0].bbus[1]])

    def set_mapping(self, remote_radio_head, baseband_units):
        self.mappings.append(Mapping(remote_radio_head, baseband_units))
