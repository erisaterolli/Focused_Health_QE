cd ..

mkdir weighted_shortest_path

for f in $(seq 0 111);
do
python3 compute_subgraph.py default shortest_path NONE patient_inputs/$f.json weighted_KG_reduced.tsv 1 all weighted_shortest_path/$f

done