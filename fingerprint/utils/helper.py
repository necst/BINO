import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_agraph import graphviz_layout
from fingerprint.enums.node_type import NodeType

def plot_fingerprint(fingerprint):
    digraph = fingerprint.digraph
    color_map = []
    for node_id in digraph.nodes():
        node = digraph.nodes[node_id]
        if node["type"] == NodeType.INITIAL:
            color_map.append('blue')
        elif node["type"] == NodeType.INTERMEDIATE:
            color_map.append('green') 
        elif node["type"] == NodeType.FINAL:
            color_map.append('red')
        elif node["type"] == NodeType.NORETURN:
            color_map.append('brown')
        elif node["type"] == NodeType.SINGULAR:
            color_map.append('yellow')
        else:
            raise Exception("Node type of %d is %d!" % (node_id, node["type"]))
    pos = graphviz_layout(digraph, prog='dot')
    nx.draw_networkx_nodes(digraph, pos, node_color=color_map)
    nx.draw_networkx_labels(digraph, pos)
    nx.draw_networkx_edges(digraph, pos)
    plt.show()