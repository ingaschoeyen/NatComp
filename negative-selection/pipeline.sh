#!/bin/bash

r=10
n=1000
overlap=0
dataset=syscalls/snd-unm/snd-unm
python3 chunking.py $dataset.train $n $overlap train.equal train.labels

for i in $(seq 1 3);
do
    # chunk test data
    python3 chunking.py $dataset.$i.test $n $overlap test.$i.chunks.data test.$i.chunks.labels
    # run negative selection algorithm for positive and negative test data
    java -jar negsel2.jar -self train.equal -n $n -o -p 0 -r $r -k -c -l -alphabet file://$dataset.alpha < test.$i.chunks.data > test.$i.chunks.scores
    # aggregate chunk scores
    python3 aggregate.py test.$i.chunks.scores test.$i.chunks.labels test.$i.scores
    # split scores into positive and negative
    python3 split.py test.$i.scores $dataset.$i.labels test.$i.pos test.$i.neg
    python3 auc.py test.$i.pos test.$i.neg fig$i.png
done

# python3 plot_auc.py posresults negresults classifier.$n.$overlap.$r.png
