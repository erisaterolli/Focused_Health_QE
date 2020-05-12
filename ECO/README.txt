This repository releases the necessary code to generates and execute queries with the ECO method proposed at:
**Focused Query Expansion with Entity Cores for Patient-Centric Health Search** paper. ECO is a novel method for query expansion, by computing entity cores that identify the most relevant and coherent terms for focused expansion. 

ECO is a framework written in python that generates and executes patient-centric focused queries given:
	- Dataframe of experimental queries containing queries title, posts, subforms together with their extracted medical entities. Refer to  Patient_Posts_With_Entities.tsv file.
	- Mapping file of medical term with medical entities code. Refer to entity_to_name.txt file. 
	- Dataframe of the medical knowledge graph. Refer to weighted_KG_reduced.tsv file
	- Query Graph given as edge list and node list for each experimental query. Refer to directory: patient_graph. To produce the Query Graphs please refer to code under Query_Graph_Extraction directory.

### How to run the code:
```
python ECO.py $QUERY_ID $RESULT_FILENAME
```

#### Arguments:
- ***QUERY_ID***: An integer within the range of the ids given to the experimental queries picked. 

- ***RESULT_FILENAME***: Filename of a json file where the results returned as a response to query number QUERY_ID by ECO method.

### One Example to Run:
```
python ECO.py 0 query_0_output.json

```


