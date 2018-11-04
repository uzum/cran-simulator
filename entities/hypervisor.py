from .switch import Switch

class Hypervisor(object):
    def __init__(self, env, id):
        self.env = env
        self.id = id
        self.bbus = []
        self.switch = Switch(self.env, type = 'internal', host = id)

    def add_baseband_unit(self, baseband_unit):
        self.bbus.append(baseband_unit)
        self.switch.add_port(baseband_unit)
