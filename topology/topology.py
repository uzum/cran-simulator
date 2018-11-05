import json

from entities.remote_radio_head import RemoteRadioHead
from entities.hypervisor import Hypervisor
from entities.baseband_unit import BasebandUnit
from entities.switch import Switch
from forwarding.forwarding import Forwarding

class Topology(object):
    def __init__(self, env):
        self.env = env
        self.rrhs = []
        self.hypervisors = []
        self.external_switch = None
        self.forwarding = Forwarding(self.env, self)
        self.setup()

    def setup(self):
        self.external_switch = Switch(self.env, 'physical', 'external')
        self.external_switch.set_forwarding_function(self.forwarding.forwarding_function)

        with open('topology/configuration.json') as f:
            configuration = json.load(f)

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
