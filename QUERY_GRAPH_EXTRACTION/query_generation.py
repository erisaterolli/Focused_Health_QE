from PMI_computation import *
from os import listdir
import random
import pandas as pd
import math
import json
import operator
import logging
import sys
import numpy as np
es = connect_elasticsearch()

def query_expansion_generation(patient_input, alpha_forum = 1.0, alpha_title = 1.0, alpha_post = 0.6, k = 10):
    query = json.load(open(patient_input, 'r'))
    subforum_dic= query["subforum"]
    for i in subforum_dic:
        subforum_entity = subforum_dic[i]
    middle_query = []
    for term in query["title"].keys():
        curr_term = '{ "match": {"aida.originalText": {"query": "'+str(term)+'", "boost": '+str(alpha_title)+'}}}'
        if curr_term not in middle_query:
            middle_query.append(curr_term)
    for term in [i for i in query["post"].values() if is_informative_entity(es, i)]:
        weight = pmi(es, term, subforum_entity)
        curr_term  = '{ "match": {"aida.allMentionEntities": {"query": "'+term+'", "boost": '+str(alpha_post * weight)+'}}}'
        if curr_term not in middle_query and term != subforum_entity:
            middle_query.append(curr_term)
    qe_query = """{"from" : 0, "size" : """+str(k)+""", "query" : { "filtered" : { "query": { "bool": { "should": [""" +','.join(middle_query)+ """]}}}}}"""
    return qe_query

def execute_query(query, result_file, result_dir):
    res = search(es, 'health-threads', query)
    with open(result_dir + result_file, 'w') as output:
        json.dump(res, output)
if __name__ == "__main__":
    inputs_dir = sys.argv[1]
    results_dir = sys.argv[2]
    for file in listdir(inputs_dir):
        query = query_expansion_generation(inputs_dir+file)
        execute_query(query, file, results_dir)
       