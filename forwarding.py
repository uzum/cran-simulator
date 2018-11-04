def find(list, fn):
    for item in list:
        if fn(item):
            return item
    return None

def forwarding_function(topology, switch, packet):
    mapping = find(topology.mappings, lambda m: m.remote_radio_head.id == packet.src)
    if (mapping == None):
        raise AttributeError('No mapping is defined for rrh id#%d' % packet.src)
    if (switch.type == 'external'):
        for hv in topology.hypervisors:
            for bbu in hv.bbus:
                if bbu.id in [baseband_unit.id for baseband_unit in mapping.baseband_units]:
                    hv.switch.put(packet)
    elif (switch.type == 'internal'):
        hypervisor = find(topology.hypervisors, lambda hv: hv.id == switch.host)
        for out in hypervisor.switch.outs:
            if out.id in [baseband_unit.id for baseband_unit in mapping.baseband_units]:
                out.put(packet)
