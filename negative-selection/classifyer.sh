#!/bin/bash
# 

r=4
n=8
overlap=3
dataset=syscalls/snd-unm/snd-unm
python3 print_stats.py $dataset.train
python3 equalise_overlap.py $dataset.train $n $overlap train.equal
posresults=()
negresults=()

for i in $(seq 1 3);
do
    python3 print_stats.py $dataset.$i.test
    # split test data into positive and negative
    python3 split.py $dataset.$i.test $dataset.$i.labels positive.test negative.test 
    python3 equalise_overlap.py positive.test $n $overlap positive.test.equal pos_labs
    python3 equalise_overlap.py negative.test $n $overlap negative.test.equal neg_labs
    # run negative selection algorithm for positive and negative test data
    java -jar negsel2.jar -self train.equal -n $n -o -p 0 -r $r -k -c -l -alphabet file://$dataset.alpha < negative.test.equal > negresults$i.txt
    java -jar negsel2.jar -self train.equal -n $n -o -p 0 -r $r -k -c -l -alphabet file://$dataset.alpha < positive.test.equal > posresults$i.txt
    python3 auc_ext.py posresults$i.txt pos_labs negresults$i.txt neg_labs > posresults$i.auc > negresults$i.auc 
    posresults+=("posresults$i.auc")
    negresults+=("negresults$i.auc")
done

python3 plot_auc.py posresults negresults classifier.$n.$overlap.$r.png 
