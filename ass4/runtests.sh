#!/bin/bash

length=$1
gens=$2

repetitions=5

for i in $(seq 1 $repetitions);
do
    python3 count_ones.py "noif-result$i.png" &
done
