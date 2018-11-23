from graphviz import Graph

parser = argparse.ArgumentParser()
parser.add_argument('--config')
args = parser.parse_args()

def plot(topology, file):
    dot = Graph('rrh topology', format="png")

    edges = set()
    for rrh in topology['remote_radio_heads']:
        dot.node(str(rrh['id']), label='r_%d' % rrh['id'])

    for rrh in topology['remote_radio_heads']:
        for bbu in rrh['baseband_units']:
            if (rrh['id'] != bbu and (bbu, rrh['id']) not in edges):
                dot.edge(str(rrh['id']), str(bbu))
                edges.add((rrh['id'], bbu))

    dot.render('%s.png' % file, view=True)
