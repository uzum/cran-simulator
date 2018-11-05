import simpy
from random import expovariate

from topology.topology import Topology

env = simpy.Environment()
topo = Topology(env)

env.run(until=1000)

for hypervisor in topo.hypervisors:
    for bbu in hypervisor.bbus:
        print('bbu id: %d' % bbu.id)
        print('packets rec: %d' % bbu.packets_rec)

for hypervisor in topo.hypervisors:
    print('switch in hypervisor: %d' % hypervisor.id)
    print('packets rec: %d' % hypervisor.switch.packets_rec)
    print('packets drop: %d' % hypervisor.switch.packets_drop)

print('external switch:')
print('packets rec: %d' % topo.external_switch.packets_rec)
print('packets drop: %d' % topo.external_switch.packets_drop)

for rrh in topo.rrhs:
    print('rrh id: %d' % rrh.id)
    print('packets sent: %d' % rrh.packets_sent)
