import pcst_fast
import pandas as pd
import re
import random
import math
import json
import operator
import logging
from elasticsearch import Elasticsearch
import pandas as pd
import numpy as np
import json
from os import listdir
from os import mkdir
import math
import operator
import sys
import string
import time

def search(es_object, index_name, search):
    res = es_object.search(index=index_name, body=search, request_timeout = 60)
    return res

def connect_elasticsearch():
    _es = None
    _es = Elasticsearch([{"host":"d5hadoop22.mpi-inf.mpg.de", "client.transport.sniff" : True, "port": 9200}])
    return _es
informative_entity_types = set(["dsyn", "patf", "sosy", "dora", "fndg", "menp", "chem", "orch", "horm", "phsu", "medd", "bhvr", "diap", 'bacs','chem', 'enzy', "inpo", "elii"])
uninformative_entity_types = set(["phpr", "npop", 'bsoj', 'idcn',"sbst", "food", "evnt", "geoa", "idcn"])

def entity_info(es_object, index_name, entity):
    res = es_object.search(index=index_name, size=1, search_type="dfs_query_then_fetch", body={"filter": { "bool" : {  "must" : [{ "term" : {"kb_id" : entity}}, { "term" : {"_type" : "entity"}} ]}}})
    return res["hits"]["hits"][0]["_source"]

def is_informative_entity(es, entity = ""):
    ei = entity_info(es, "health-kb", entity)
    types = []
    if("types" in ei.keys()):
        types = [str(x) for x in ei["types"]]
    return is_informative_types(types)

def is_informative_types(types = []):
    return len(set(types).intersection(informative_entity_types)) > 0 or len([x for x in types if x.startswith("disease_affecting") or x.startswith("symptoms")]) > 0
def is_informative_type(t):
    return len(t) >4 and not t.startswith("interactions")
def count_co_occurrences(es, e1, e2):
    res = es.count(index="health-threads", body={"query": {"bool": {"must": [ { "term" : { "aida.allEntities" : e1 } },{ "term" : { "aida.allEntities" : e2}}, {"regexp": {"FeedUrl":".*(healthboards|ehealthforum|patient.co).*"}}]}}})
    return res[u'count']

def count_occurrences(es, entity):
    res = es.count(index="health-threads", body={"query": {"bool": {"must":[{ "term" : { "aida.allEntities" : entity }}, {"regexp": {"FeedUrl":".*(healthboards|ehealthforum|patient.co).*"}}]}}})
    return res[u'count']


def pmi(es, e1, e2, variant=2):
    e1_occ = count_occurrences(es, e1)
    e2_occ = count_occurrences(es, e1)
    cocc = float(count_co_occurrences(es, e1, e2))
    all_occ = float(1048428)
    if cocc == 0:
        pmi_uv =  0
    else:
        pmi = math.log(cocc) - math.log(e1_occ) - (math.log(e2_occ) - math.log(all_occ))
        if(variant == 2):
            pmi_uv =  abs(round(pmi + (math.log(cocc) - math.log(all_occ)),3))
    return pmi_uv

def get_types(es, entity):
    ei = entity_info(es, "health-kb", entity)
    types = []
    if("types" in ei.keys()):
        types = [str(x) for x in ei["types"]]
    return types
def compute_tf(es, entity, subforum):
    query = """{"size":100000,"_source": ["aida.allMentionEntities"], "query": {"bool": {"must":[{"match": {"aida.allMentionEntities": \""""+entity+"""\"}},{ "match_phrase": {"Description":\""""+subforum+"""\"}},{ "match_phrase": {"FeedUrl": "http://ehealthforum.com/"}}]}}}"""
    res = search(es,"health-docs-v2", query)
    tf = 0
    for hit in res["hits"]["hits"]:
        hit_id = hit["_id"]
        tf += hit["_source"]["aida"]["allMentionEntities"].split(" ").count(entity)
    return tf
def compute_idf(es, entity):
    query = """{"size": 0,"_source": "Description", "query": {"bool": {"must":[{ "match": {"FeedUrl": "http://ehealthforum.com/"}},{"match": {"aida.allMentionEntities": \""""+entity+"""\"}}]}},"aggs" : {"subforum_frequency" : {"cardinality" : {"field" : "Description"}}}}"""
    res = search(es, "health-docs-v2",  query)
    return res["aggregations"]["subforum_frequency"]["value"]
def unique_subforums(es):
    res = search(es, "health-docs-v2", {"size":300000,"_source": "Description", "query": {"bool": {"must": [{"match": {"FeedUrl": "http://ehealthforum.com/"}}]}}})
    sub_dic = {}
    for hit in res["hits"]["hits"]:
        [parent,forum] = hit["_source"]["Description"].split("\n-")
        sub_dic[forum] = parent+"\n-"+forum
    return sub_dic
def get_mayoclinic_encylopedia(es):
    res = search(es, "health-docs-v2", {"from" : 0, "size" : 3100, "_source": ["Title","aida.annotatedText"],    "query" : { "filtered" : { "query": { "bool": { "must" : [{"regexp": {"FeedUrl": ".*mayoclinic.*"}}]}}}}})
    ency_dic = {}
    for hit in res["hits"]["hits"]:
        title = hit["_source"]["Title"]
        try:
            text = ''.join(hit["_source"]["aida"]["annotatedText"].split("\n\n")[3:5])
            ency_dic[title] = text
        except:
            pass
    return ency_dic
es = connect_elasticsearch()


def query_expansion_generation(subforum, title_terms, qe_entities, alpha_title = 1.0, alpha_post = 0.65, k = 10):
    middle_query = []
    for term in title_terms:
        curr_term = '{ "match": {"aida.originalText": {"query": "'+str(term)+'", "boost": '+str(alpha_title)+'}}}'
        if curr_term not in middle_query:
            middle_query.append(curr_term)
    for term in qe_entities + [subforum]:
        weight = pmi(es, term, subforum)
        curr_term  = '{ "match": {"aida.allMentionEntities": {"query": "'+term+'", "boost": '+str(alpha_post)+'}}}'
        if curr_term not in middle_query and term != subforum:
            middle_query.append(curr_term)
    qe_query = """{"from" : 0, "size" : """+str(k)+""", "query" : { "filtered" : { "query": { "bool": { "should": [""" +','.join(middle_query)+ """]}}}}}"""
    return qe_query

def execute_query(query, result_file):
    res = search(es, 'health-threads', query)
    with open(result_file, 'w') as output:
        json.dump(res, output)


queries = pd.read_csv("Patient_Posts_With_Entities.tsv", delimiter = "\t")




edge_weights = pd.read_csv("weighted_KG_reduced.tsv", delimiter = "\t")


nodes_names = {}
with open("entity_to_name.txt", "r") as f:
    for line in f:
        s = line[:-1].split(" ")
        nodes_names[s[0]] = ' '.join(s[1:])



u = edge_weights.u.tolist()
v = edge_weights.v.tolist()
labels = edge_weights.label.tolist()
dist = edge_weights.dist_pmi.tolist()
uv_w = {('_'.join(sorted([u[i],v[i]]))):dist[i] for i in range(len(u))}
uv_l = {('_'.join(sorted([u[i],v[i]]))):labels[i] for i in range(len(u))}



query_entities = {}


for query in [int(sys.argv[1])]:
    e1 = []
    e2 = []
    with open("patient_graph/"+str(query)+"_edges.txt", "r") as f:
        for line in f:
            (u,v) = line.split(" ")[:2]
            e1.append(u)
            e2.append(v)
    current_query = queries[queries["Patient_Id"] == query]
    subforum = current_query["Entity"].tolist()[0]
    forum_name = current_query["Condition"].tolist()[0]
    title_keywords = current_query["Filtered_Post_Title"].tolist()[0].split(" ")
    nodes = list(set(e1 + e2 + [subforum]))
    nodes_dic = {nodes[i]:i for i in range(len(nodes))}
    ids_dic = {i:nodes[i] for i in range(len(nodes))}
    edges = []
    cost = []
    for i,j in zip(e1, e2):
        edges.append([nodes_dic[i], nodes_dic[j]])
        [i,j] = [s for s in sorted([i,j])] 
        cost.append(pmi(es, i, j, variant=2))
    norm_costs = [(1 - i/max(cost)) for i in cost]
    root_id = nodes_dic[subforum]
    tf_idf = [compute_tf(es,i,forum_name)*(1.0/compute_idf(es,i)) if compute_idf(es,i) != 0 else 0  for i in nodes]
    v_tfidf = {nodes[i]:tf_idf[i]/max(tf_idf) for i in range(len(nodes))}
    prizes = []
    for i in nodes:
        prizes.append(v_tfidf[i])
    vertices_st, edges_st = pcst_fast.pcst_fast(np.array(edges), np.array(prizes), np.array(cost), root_id, 1, "strong", 0)
    entities = [ids_dic[i] for i in vertices_st if is_informative_entity(es, ids_dic[i]) ]
    es_query = query_expansion_generation(subforum, title_keywords, entities)
    execute_query(es_query, sys.argv[2])