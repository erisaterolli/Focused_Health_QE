import json
import networkx as nx
import pandas as pd
from extract_entities import extract_entities_from_file, extract_entities_from_json
from PMI_computation import is_informative_entity, es
import queue


def read_knowledge_base(file_address='weighted_KG_reduced.tsv', weight_column='dist_pmi', weight_file='edge_weights.txt', name_file='names.txt', has_label=True):
    import json
    df = pd.read_csv(file_address, sep="\t")
    weight_dict = dict()
    label_dict = dict()
    out_file_weight = open(weight_file, 'w')
    #out_file_name = open(name_file, 'w')
    for index, row in df.iterrows():
        u = row['u']
        v = row['v']
        weight = float(row[weight_column])
        weight_dict[(u,v)] = weight
    weight_dict = dict((':'.join(k), v) for k,v in weight_dict.items())
    return weight_dict


def make_knowledgebase_graph(kb_address):
    edges = read_knowledge_base(kb_address)
    base = nx.Graph()
    for line in edges:
        edge = line.split(":")
        base.add_edge(edge[0], edge[1], weight=float(edges[line]))
    return base


def make_graph(all_entities, kb_address):
    base = make_knowledgebase_graph(kb_address)
    g = base.subgraph(all_entities)
    return g


def color_the_graph(input_address, g, map_to_name={}):

    result_entities = []
    forum_ent, post_ent, title_ent, neighbors = extract_entities_from_file(input_address)

    for entity in g:
        if entity in map_to_name:
            g.node[entity]['label'] = map_to_name[entity]
        if entity in forum_ent:
            g.node[entity]['viz'] = {'color': {'r': 255, 'g': 0, 'b': 0, 'a': 0}}
        elif entity in title_ent:
            g.node[entity]['viz'] = {'color': {'r': 0, 'g': 100, 'b': 0, 'a': 0}}
        elif entity in post_ent:
            g.node[entity]['viz'] = {'color': {'r': 0, 'g': 100, 'b': 200, 'a': 0}}
        elif entity in result_entities:
            g.node[entity]['viz'] = {'color': {'r': 150, 'g': 0, 'b': 150, 'a': 0}}
        elif entity in neighbors:
            g.node[entity]['viz'] = {'color': {'r': 255, 'g': 165, 'b': 0, 'a': 0}}
    return g


def add_path_for_bfs(graph, entity, par):
    ent = entity
    while par[ent] != ent:
        graph.append(ent)
        ent = par[ent]
    return graph


def dijkstra(graph, source, kb_address='weighted_KG_reduced.tsv'):
    nodes = list(graph.nodes)
    base_graph = make_knowledgebase_graph(kb_address)
    component_num = dict()
    p = list(nx.connected_components(graph))
    cmp_num = 0
    mark = dict()

    for c in p:
        for x in c:
            component_num[x] = cmp_num
        cmp_num += 1

    source_comp = component_num[source]
    for x in list(graph.nodes):
        cmp_num = component_num[x]
        if cmp_num == source_comp:
            mark[cmp_num] = True
        else:
            mark[cmp_num] = False

    new_graph = []
    start_weight = 1000000000
    parents = dict()
    distances = dict()
    q = queue.PriorityQueue()
    remained = graph.number_of_nodes() - len(new_graph)
    for x in list(base_graph.nodes):
        weight = start_weight
        par = None
        if x in component_num and component_num[x] == source_comp:
            weight = 0
            par = x
            q.put(([0, x]))
        distances[x] = weight
        parents[x] = par
    previous_nodes = list(graph.nodes)
    while not q.empty():
        v_tuple = q.get()
        v = v_tuple[1]
        for vertex in base_graph[v]:
            weight = base_graph[v][vertex]['weight']
            candidate_distance = distances[v] + weight
            if distances[vertex] > candidate_distance:
                distances[vertex] = candidate_distance
                parents[vertex] = v
                if candidate_distance < -1000:
                    raise Exception("Negative cycle detected")
                q.put(([distances[vertex], vertex]))
                entity = vertex
                if entity in nodes and not mark[component_num[entity]]:
                        remained -= 1
                        new_graph = add_path_for_bfs(new_graph, entity, parents)
                        mark[component_num[entity]] = True
        all_ok = True
        for j in list(graph.nodes):
            if not mark[component_num[j]]:
                all_ok = False
        if all_ok:
            return list(set(previous_nodes + new_graph))
    return list(set(previous_nodes + new_graph))


def bfs(graph, source, kb_address='weighted_KG_reduced.tsv'):
    nodes = list(graph.nodes)
    base_graph = make_knowledgebase_graph(kb_address)
    component_num = dict()
    p = list(nx.connected_components(graph))
    cmp_num = 0
    dis = dict()
    par = dict()
    queue = list()
    new_graph = list()
    mark = dict()
    source_comp = 0
    previous_nodes = list(graph.nodes)
    for c in p:
        for x in c:
            component_num[x] = cmp_num
            if x == source:
                source_comp = cmp_num
        cmp_num += 1
    for x in list(graph.nodes):
        cmp_num = component_num[x]
        if cmp_num == source_comp:
            new_graph.append(x)
            par[x] = x
            dis[x] = 0
            mark[cmp_num] = True
            queue.append(x)
        else:
            mark[cmp_num] = False
    remained = graph.number_of_nodes() - len(new_graph)
    while len(queue) > 0:
        top = queue.pop(0)
        if top in base_graph:
            neighbors = [n for n in base_graph.neighbors(top)]
            for entity in neighbors:
                if entity not in dis:
                    dis[entity] = dis[top] + 1
                    par[entity] = top
                    queue.append(entity)
                    if entity in nodes and not mark[component_num[entity]]:
                        remained -= 1
                        new_graph = add_path_for_bfs(new_graph, entity, par)
                        mark[component_num[entity]] = True
            all_ok = True
            for j in list(graph.nodes):
                if not mark[component_num[j]]:
                    all_ok = False
            if all_ok:
                return list(set(previous_nodes + new_graph))
        else:
            print('base graph is not complete', top)
    return list(set(previous_nodes + new_graph))
