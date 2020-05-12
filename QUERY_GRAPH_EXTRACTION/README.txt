# QUERY GRAPH CONSTRUCTION 

QG is a framework that computes the Query Graph for a given patient query given:
   - Patient query's entities (forum entities, title entities, post entities).
   - Medical Knowledge graph.
 

### How to run the code:
```
python3 compute_subgraph.py $PATIENT_GRAPH_TYPE $SUBGRAPH_METHOD $EXTRACTION_METHOD $PATIENT_INPUT_FILE.json $KNOWLEDGE_BASE_FILE_ADDRESS  $WEIGHTING_STATUS $OUT_PUT_FORMAT $OUT_PUT_FILE_ADDRESS
```

#### Arguments:
- ***PATIENT_GRAPH_TYPE***:

    1. default: create the query graph by considering the subforum entity + title entities + post entities and the relations between them.
    2. with_forum_neighbors: same as default but add also neighbours of the subform entity.

<br />

- ***SUBGRAPH_METHOD***:
    1. forum_component: compute the connected component of the patient graph that contains the subforum entity.
    2. shortest_path: make the patient graph connected using shortest path via the forum's component to other components. (it could be wighted or unweighted algorithm based on $WEIGHTING_STATUS)
<br />

- ***EXTRACTION_METHOD***:
    1. NONE: It will returns the result of the subgraph method itself.
    2. steinter_tree: It will returns an approximate steiner tree that contains subforum + title entities.
<br />

- ***PATIENT_INPUT_FILE.json***:
    - Address to a json file that contains entities from the subforum, title and post. An example is available in the patient_inputs directory.
<br />

- ***KNOWLEDGE_BASE_FILE_ADDRESS***:
    - Address to a text file that should be formatted like a dataframe that each row shows an edge and it should contains at least these 3 columns:
        - u: the first vertex of the edge.
        - v: the second vertex of the edge.
        - weight: the weight of the vertex (It should be a distance metric.)
<br />

- ***WEIGHTING_STATUS***:
    - A boolean factor that can be 1 or 0. It shows whether we should assume the graph as a weighted graph or not (1=True and 2=False).
<br />

- ***OUT_PUT_FORMAT***:
    1. edge_list: Write the result as an edge_list of the result subgraph.
    2. node_list: Write the result as the list of nodes of the result subgraph.
    3. gexf: Write the colored result subgraph as a gexf format, so it can be plotted in networkx and gephi.
    4. all: Write all the results together.
<br />

- ***OUT_PUT_FILE_ADDRESS***: Address of the file that the result should be writed there.

<br />



# IMPORTANT NOTE:
Before running anything run the function in utils/write_edge_and_names with your input knowledge graph. This step will hash the edge_weight dictionary and make the other functions faster (they will read a pickle file named weights.txt for weights). Then run an algorithm.


### One Example to Run:
```
python3 compute_subgraph.py default shortest_path NONE patient_inputs/0.json weighted_KG_reduced.tsv 0 edge_list list.txt

```
