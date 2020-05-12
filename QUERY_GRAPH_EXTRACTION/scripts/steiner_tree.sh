cd ..

mkdir steiner_weighted_neighbors

for f in $(seq 64 65);
do
python3 compute_subgraph.py with_forum_neighbors shortest_path steinter_tree patient_inputs/$f.json weighted_KG_reduced.tsv 0 all steiner_weighted_neighbors/$f

done