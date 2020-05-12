from os import listdir
import random
import pandas as pd
import math
import json
import operator
import logging
import sys
import numpy as np
def compute_precision_at_k(l, k):
    l = l[:k]
    return sum(l)/k
def compute_map_at_k(l, k):
    ap = []
    for s in range(1, k+1):
        ap.append(compute_precision_at_k(l, s))
    return sum(ap)/len(ap)
def compute_ndcg(l, k):
    l = l[:k]
    dcg = sum(([(math.pow(2, l[i]) - 1) / math.log(i + 2, 2) for i in range(len(l))]))
    sorted_l = sorted(l, reverse = True)
    idcg = sum(([(math.pow(2, sorted_l[i]) - 1) / math.log(i + 2, 2) for i in range(len(sorted_l))]))
    if (idcg > 0):
        return dcg/idcg
    else:
        return float(0)
def compute_mrr(l, k):
    return sum([l[i]*float(1)/float(i + 1) for i in range(len(l))])/k

def compute_eval_metrics(groundtruth, results_dir, k):
    all_judgment = pd.read_csv(groundtruth)
    relevance_dic = {}
    unrelevance_dic = {}
    for patient, group in all_judgment.groupby(["patient_id"]):
        relevance_dic[patient] = [i for i in group[group['relevance_judgement'] == True]['hit_id'].tolist()]
        unrelevance_dic[patient] = [i for i in group[group['relevance_judgement'] == False]['hit_id'].tolist()]
    precision_at_k = []
    ndcg_at_k = []
    map_at_k = []
    mrr_at_k = []
    general_results = pd.DataFrame(columns = ["P@"+str(k), "MAP@"+str(k), "NDCG@"+str(k), "MRR"])
    for file in listdir(results_dir):
        patient_hits = []
        with open(results_dir+file, "r") as f:
            hits = [i["_id"]  for i in json.loads(f.read())["hits"]["hits"][:k] ]
            rel =0
            unrel = 0
            miss_jud = 0
            for hit in hits:
                if hit in relevance_dic[patient]:
                    patient_hits.append(1)
                    rel += 1
                elif hit in unrelevance_dic[patient]:
                    patient_hits.append(0)
                    unrel += 1
                else:
                    miss_jud += 1
            p = round(compute_precision_at_k(patient_hits, k),2)
            m = round(compute_map_at_k(patient_hits, k),2)
            n = round(compute_ndcg(patient_hits, k),2)
            mrr= round(compute_mrr(patient_hits, k),2)
            general_results.loc[file] = [p, m, n, mrr]
    return general_results.mean()


if __name__ == "__main__":
    ground_truth = sys.argv[1]
    results_dir = sys.argv[2]
    print(compute_eval_metrics(ground_truth, results_dir, k = 5))