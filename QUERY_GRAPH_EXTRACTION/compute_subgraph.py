import sys
from functions import get_forum_component, unweighted_shortest_path, weighted_shortest_path
from subgraph_extraction import steiner_tree_extraction
from extract_entities import extract_entities_from_file


def extract_sub_graph(graph_type, sub_graph_method, extract_func, input_address, kb_address, weighting_status, out_put_func, out_put_file):
    if sub_graph_method == 'forum_component':
        if extract_func == 'steinter_tree':
            comp = get_forum_component(graph_type, input_address, kb_address, 'graph', '')
            forum, topic, post = extract_entities_from_file(input_address)
            steiner_tree_extraction(comp, list(set(forum + topic)), kb_address, out_put_func, out_put_file)
        elif extract_func == 'PCST':
            comp = get_forum_component(graph_type, input_address, 'graph', '')
        else:
            get_forum_component(graph_type, input_address, kb_address, out_put_func, out_put_file)
    if sub_graph_method == 'shortest_path':
        if weighting_status == '0':
            if extract_func == 'steinter_tree':
                comp = unweighted_shortest_path(graph_type, input_address, kb_address, 'graph', '')
                forum, topic, post, neighbors = extract_entities_from_file(input_address)
                steiner_tree_extraction(comp, input_address, list(set(forum + topic)), out_put_func, out_put_file)
            elif extract_func == 'PCST':
                comp = unweighted_shortest_path(graph_type, input_address, kb_address, 'graph', '')
            else:
                unweighted_shortest_path(graph_type, input_address, kb_address, out_put_func, out_put_file)
        else:
            if extract_func == 'steinter_tree':
                comp = weighted_shortest_path(graph_type, input_address, kb_address, 'graph', '')
                forum, topic, post, neighbors = extract_entities_from_file(input_address)
                steiner_tree_extraction(comp, input_address, list(set(forum + topic)), out_put_func, out_put_file)
            elif extract_func == 'PCST':
                comp = weighted_shortest_path(graph_type, input_address, kb_address, 'graph', '')
            else:
                weighted_shortest_path(graph_type, input_address, kb_address, out_put_func, out_put_file)

if __name__ == "__main__":
    graph_type = sys.argv[1]
    sub_graph_method = sys.argv[2]
    extract_func = sys.argv[3]
    input_address = sys.argv[4]
    kb_address = sys.argv[5]
    weighting_status = sys.argv[6]
    out_put_func = sys.argv[7]
    out_put_file = sys.argv[8]
    extract_sub_graph(graph_type, sub_graph_method, extract_func, input_address, kb_address, weighting_status, out_put_func, out_put_file)
