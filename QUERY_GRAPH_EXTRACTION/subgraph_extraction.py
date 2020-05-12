import pandas as pd
import pickle
from networkx.algorithms.approximation.steinertree import steiner_tree
from extract_entities import extract_entities_from_file
import networkx as nx
from utils import color_the_graph


def steiner_tree_extraction(g, input_file, selected_input, out_put_func, out_put_file, weight_file='weights.txt'):
    file = open(weight_file, 'rb')
    weights = pickle.load(file)
    max_weight = 0
    for u,v,d in g.edges(data=True):

        if (u,v) in weights:
            d['weight'] = weights[(u,v)]
            max_weight = max(max_weight, d['weight'])
        elif (v,u) in weights:
            d['weight'] = weights[(v,u)]
            max_weight = max(max_weight, d['weight'])
    for u,v,d in g.edges(data=True):
        if max_weight != 0:
            d['weight'] = (max_weight - d['weight'])/max_weight
        else:
            print('max weight is zero!')
    forum, title, post, neighbors = extract_entities_from_file(input_file)
    selected = list(set(forum + title))
    print(g.number_of_nodes, g.number_of_edges())
    tree = steiner_tree(g, selected)
    print(len(selected))
    print(tree.number_of_nodes, tree.number_of_edges())
    if out_put_func == 'edge_list':
        nx.write_edgelist(tree, out_put_file)
    elif out_put_func == 'node_list':
        f = open(out_put_file, 'w')
        f.write("%s\n" % list(tree.nodes))
    elif out_put_func == 'all':
        to_plot = color_the_graph(input_file, tree)
        nx.write_gexf(to_plot, "%s_plots.gexf"%out_put_file)
        f = open("%s_nodes.txt"%out_put_file, 'w')
        f.write("%s\n" % list(tree.nodes))
        nx.write_edgelist(tree, "%s_edges.txt"%out_put_file)
