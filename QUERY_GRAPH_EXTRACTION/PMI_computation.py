from os import listdir
import random
import pandas as pd
import math
import json
import operator
import logging
from elasticsearch import Elasticsearch
import pandas as pd
import numpy as np
import json
from nltk import wordnet
from os import listdir
from os import mkdir
import random
import math
import json
import operator
import sys
import string


def search(es_object, index_name, search):
    res = es_object.search(index=index_name, body=search)
    return res


def connect_elasticsearch():
    _es = None
#     _es = Elasticsearch([{"host":"d5hadoop29.mpi-inf.mpg.de", "port": 9200}])
    _es = Elasticsearch([{"host":"d5hadoop22.mpi-inf.mpg.de", "client.transport.sniff" : True, "port": 9200}])
    return _es

informative_entity_types = set(["dsyn", "patf", "sosy", "dora", "fndg", "menp", "chem", "orch", "horm", "phsu", "medd", "bhvr", "diap", 'bacs','chem', 'enzy', "inpo", "elii"])
uninformative_entity_types = set(["bpoc", "phpr", "npop", 'bsoj', 'idcn',"sbst", "food", "evnt", "geoa", "idcn"])


def entity_info(es_object, index_name, entity):
    res = es_object.search(index=index_name, size=1, search_type="dfs_query_then_fetch",_source_include=["human_readable", "types"], body={"filter": { "bool" : {  "must" : [{ "term" : {"kb_id" : entity}}, { "term" : {"_type" : "entity"}} ]}}})
    if len(res["hits"]["hits"]) < 1:
        return False
    return res["hits"]["hits"][0]["_source"]


def is_informative_entity(es, entity = ""):
    ei = entity_info(es, "health-kb", entity)
    if ei == False:
        return False
    types = []
    if("types" in ei.keys()):
        types = [str(x) for x in ei["types"]]
        #print(types)
    return is_informative_types(types)

# def is_informative_types(types = []):
#     return len(set(types).intersection(informative_entity_types)) > 0
def is_informative_types(types = []):
    return len(set(types).intersection(informative_entity_types)) > 0 or len([x for x in types if x.startswith("disease_affecting") or x.startswith("symptoms")]) > 0
def is_informative_type(t):
    return len(t) >4 and not t.startswith("interactions")
def count_co_occurrences(es, e1, e2):
    res = es.count(index="health-docs", body={"query": {"bool": {"must": [ { "term" : { "aida.allEntities" : e1 } },{ "term" : { "aida.allEntities" : e2}}, {"regexp": {"FeedUrl":".*(healthboards|ehealthforum|patient.co).*"}}]}}})
    return res[u'count']

def count_occurrences(es, entity):
    res = es.count(index="health-docs", body={"query": {"bool": {"must":[{ "term" : { "aida.allEntities" : entity }}, {"regexp": {"FeedUrl":".*(healthboards|ehealthforum|patient.co).*"}}]}}})
    return res[u'count']

# def count_all(es, entity):
#     res = es.count(index="health-docs", body={"query" : {"constant_score" : { "filter" : { "exists" : { "field" :"allEntities"}}}}})
#     return res[u'count']

def pmi(es, e1, e2, variant=2):
    cocc = float(count_co_occurrences(es, e1, e2))
    e1_occ = float(count_occurrences(es, e1))
    e2_occ = float(count_occurrences(es, e2))
    all_occ = float(1048428)
     #math.log((cocc/e1_occ)/(e2_occ/all_occ))
     #math.log(cocc/e1_occ) - math.log(e2_occ/all_occ)
#     print("coocc: {}, e1 occ: {}, e2 occ: {}, all occ: {}".format(cocc,e1_occ, e2_occ, all_occ))
    if cocc == 0:
        return -100
    pmi = math.log(cocc) - math.log(e1_occ) - (math.log(e2_occ) - math.log(all_occ))
    if(variant == 2):
        return pmi + (math.log(cocc) - math.log(all_occ))
    return pmi


def get_types(es, entity):
    ei = entity_info(es, "health-kb", entity)
    types = []
    if("types" in ei.keys()):
        types = [str(x) for x in ei["types"]]
    return types

es = connect_elasticsearch()
#print(is_informative_entity(es, 'C0233535'))