cd ..

mkdir unweighted_shortest_path

for f in $(seq 0 111);
do
python3 compute_subgraph.py default shortest_path NONE patient_inputs/$f.json weighted_KG_reduced.tsv 0 all unweighted_shortest_path/$f

done