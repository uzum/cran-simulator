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

    def find_baseband_unit(self, id):
        for bbu in self.bbus:
            if (bbu.id == id):
                return bbu
        return None

    def remove_baseband_unit(self, baseband_unit):
        self.bbus.remove(baseband_unit)
        self.switch.remove_port(baseband_unit)
