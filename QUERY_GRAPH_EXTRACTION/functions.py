import networkx as nx
import pandas as pd
from extract_entities import extract_entities_from_tsv, extract_entities_from_list, extract_entities_from_file
from PMI_computation import *
from utils import color_the_graph, make_graph, bfs, dijkstra


def get_forum_component(graph_type, input_address, kb_address, out_put_func, out_put_file):

    forum_ent, title_ent, post_ent, neighbors = extract_entities_from_file(input_address)
    print(forum_ent)
    all_entities = list(set(post_ent + title_ent + forum_ent))
    if graph_type == 'with_forum_neighbors':
        all_entities = list(set(all_entities + neighbors))
    g = make_graph(all_entities, kb_address)
    comp = nx.node_connected_component(g, forum_ent[0])
    connected_comp = g.subgraph(list(comp))
    if out_put_func == 'gexf':
        to_plot = color_the_graph(input_address, connected_comp)
        nx.write_gexf(to_plot, out_put_file)
    elif out_put_func == 'edge_list':
        nx.write_edgelist(connected_comp, out_put_file)
    elif out_put_func == 'node_list':
        f = open(out_put_file, 'w')
        f.write("%s\n" % list(connected_comp.nodes))
    elif out_put_func == 'all':
        to_plot = color_the_graph(input_address, connected_comp)
        nx.write_gexf(to_plot, "%s_plots.gexf"%out_put_file)
        f = open("%s_nodes.txt"%out_put_file, 'w')
        f.write("%s\n" % list(connected_comp.nodes))
        nx.write_edgelist(connected_comp, "%s_edges.txt"%out_put_file)
    elif out_put_func == 'graph':
        return connected_comp


def weighted_shortest_path(graph_type, input_address, kb_address, out_put_func, out_put_file):
    forum_ent, title_ent, post_ent, neighbors = extract_entities_from_file(input_address)
    all_entities = list(set(post_ent + title_ent + forum_ent))
    if graph_type == 'with_forum_neighbors':
        all_entities = list(set(all_entities + neighbors))
    g = make_graph(all_entities, kb_address)
    res = dijkstra(g, forum_ent[0], kb_address)
    connected_comp = make_graph(res, kb_address)
    if out_put_func == 'gexf':
        to_plot = color_the_graph(input_address, connected_comp)
        nx.write_gexf(to_plot, out_put_file)
    elif out_put_func == 'edge_list':
        nx.write_edgelist(connected_comp, out_put_file)
    elif out_put_func == 'node_list':
        f = open(out_put_file, 'w')
        f.write("%s\n" % list(connected_comp.nodes))
    elif out_put_func == 'all':
        to_plot = color_the_graph(input_address, connected_comp)
        nx.write_gexf(to_plot, "%s_plots.gexf"%out_put_file)
        f = open("%s_nodes.txt"%out_put_file, 'w')
        f.write("%s\n" % list(connected_comp.nodes))
        nx.write_edgelist(connected_comp, "%s_edges.txt"%out_put_file)
    elif out_put_func == 'graph':
        return connected_comp


def unweighted_shortest_path(graph_type, input_address, kb_address, out_put_func, out_put_file):

    forum_ent, title_ent, post_ent, neighbors = extract_entities_from_file(input_address)
    all_entities = list(set(post_ent + title_ent + forum_ent))
    if graph_type == 'with_forum_neighbors':
        all_entities = list(set(all_entities + neighbors))
    g = make_graph(all_entities, kb_address)
    bfs_res = bfs(g, forum_ent[0], kb_address)

    connected_comp = make_graph(bfs_res, kb_address)

    if out_put_func == 'gexf':
        to_plot = color_the_graph(input_address, connected_comp)
        nx.write_gexf(to_plot, out_put_file)
    elif out_put_func == 'edge_list':
        nx.write_edgelist(connected_comp, out_put_file)
    elif out_put_func == 'node_list':
        f = open(out_put_file, 'w')
        f.write("%s\n" % list(connected_comp.nodes))
    elif out_put_func == 'all':
        to_plot = color_the_graph(input_address, connected_comp)
        nx.write_gexf(to_plot, "%s_plots.gexf"%out_put_file)
        f = open("%s_nodes.txt"%out_put_file, 'w')
        f.write("%s\n" % list(connected_comp.nodes))
        nx.write_edgelist(connected_comp, "%s_edges.txt"%out_put_file)
    elif out_put_func == 'graph':
        return connected_comp

