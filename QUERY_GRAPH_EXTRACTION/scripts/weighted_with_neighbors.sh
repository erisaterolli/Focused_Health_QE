cd ..

mkdir weighted_shortest_path_with_neighbors

for f in $(seq 0 111);
do
python3 compute_subgraph.py with_forum_neighbors shortest_path NONE patient_inputs/$f.json weighted_KG_reduced.tsv 0 all weighted_shortest_path_with_neighbors/$f

done

