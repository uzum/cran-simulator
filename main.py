import simpy
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('config')
args = parser.parse_args()


from topology.topology import Topology

env = simpy.Environment()
topo = Topology(env, args.config)

env.run()

print('-------BBU STATS----------')
for hypervisor in topo.hypervisors:
    for bbu in hypervisor.bbus:
        print('bbu id: %d' % bbu.id)
        print('packets rec: %d' % bbu.packets_rec)
        print('average wait: %f' % (sum(bbu.waits) / float(len(bbu.waits))))
        print('average arrival: %f' % (sum(bbu.arrivals) / float(len(bbu.arrivals))))
        print('\n')
print('--------------------------\n\n')

print('-------OVS-SWITCHES-------')
for hypervisor in topo.hypervisors:
    print('switch in hypervisor: %d' % hypervisor.id)
    print('packets rec: %d' % hypervisor.switch.packets_rec)
    print('packets drop: %d' % hypervisor.switch.packets_drop)
print('-------------------------\n\n')

print('-----EXT-SWITCH--------')
print('packets rec: %d' % topo.external_switch.packets_rec)
print('packets drop: %d' % topo.external_switch.packets_drop)
print('------------------------\n\n')

print('-------RRH STATS--------')
for rrh in topo.rrhs:
    print('rrh id: %d' % rrh.id)
    print('packets sent: %d' % rrh.packets_sent)
