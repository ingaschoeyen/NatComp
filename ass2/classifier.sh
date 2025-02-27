#!/bin/bash
# 

r=4
n=8
overlap=3
dataset=syscalls/snd-unm/snd-unm
python3 print_stats.py $dataset.train
python3 equalise_overlap.py $dataset.train $n $overlap train.equal
results=()

for i in $(seq 1 3);
do
    python3 print_stats.py $dataset.$i.test
    python3 equalise_overlap.py $dataset.$i.test $n $overlap test.equal test_indx
    # run negative selection algorithm for chunked data
    java -jar negsel2.jar -self train.equal -n $n -o -p 0 -r $r -k -c -l -alphabet file://$dataset.alpha < test.equal > results$i.txt
    python3 auc_ext.py results$i.txt test_indx $dataset.$i.labels > results$i.auc
    results+=("results$i.auc")
done

python3 plot_auc.py results classifier.$n.$overlap.$r.png 
