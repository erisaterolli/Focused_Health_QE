import json
import pandas as pd
from pandas import DataFrame
from PMI_computation import *
es = connect_elasticsearch()


def extract_entities_from_file(file_name):
    f = open('%s'%file_name, 'r')
    j = json.load(f)
    forum = j['subforum']
    post = j['post']
    title = j['title']
    neighbors = dict()
    if 'top_neighbors' in j:
        neighbors = j['top_neighbors']

    return list(forum.keys()), list(title.keys()), list(post.keys()), list(neighbors.values())


def extract_entities_from_list(query_number):

    '''
    :param query_number
    :return: a list that contains the topic entity, if it's informative, empty list otherwise.
    '''
    df = DataFrame.from_csv("data/Patient_Lists_With_Entities.tsv", sep="\t")
    ent = df['Entity'].tolist()[query_number]
    print('forum:', ent)
    if is_informative_entity(es, ent):
        return [ent]
    else:
        return []


def extract_entities_from_json(json_name, number_of_results=10):

    '''
    find entities in top results for given json.file.

    :param
    json_name: name of the json file that placed in data data/Expansion_Hits_Top10 file.
    :param
    number_of_results: number of results should be assumed as top results.
    :return:
    list of entities in top results.
    '''

    entities = []
    json_file = open("data/Expansion_Hits_Top10/%s" % json_name)
    js = json.load(json_file)
    hits = js['hits']
    top_results = hits['hits'][:number_of_results]
    row = 0
    for result in top_results:
        row += 1
        source = result['_source']
        all_entities = source['aida']['allEntities']
        for x in all_entities:
            if is_informative_entity(es, x):
                entities.append((x, row))
    return entities


def extract_entities_from_tsv(query_number):


    '''

    :param query_number:
    :return: two list, first one is the list of informative entities in post, and second one is the list of informative
    entities in the post.
    '''
    df = DataFrame.from_csv("data/Patient_Posts_With_Entities.tsv", sep="\t")

    posts = df['Post_Entities'].tolist()
    titles = df['Title_Entities'].tolist()
    entities = []
    title_entities = []
    post = posts[query_number]
    title = titles[query_number]
    entity_ids = post.split("_")[1::2]
    title_ids = title.split("_")[1::2]
    title_entities = title_entities + title_ids
    entities = entities + entity_ids

    valid_entities = []
    valid_title = []
    for entity in entities:
        if is_informative_entity(es, entity):
            valid_entities.append(entity)
    for entity in title_entities:
        if is_informative_entity(es, entity):
            valid_title.append(entity)
    return valid_entities, valid_title
