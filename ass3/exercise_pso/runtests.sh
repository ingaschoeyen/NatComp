#!/bin/bash

declare -a benchmarks=("airplane" "peppers" "lenna" "mandril")

k=$1
n=$2
maxit=$3
omega=$4
alphaone=$5
alphatwo=$6
eps="100"

# how many times to compute the pso
repetitions=5


for benchmark in "${benchmarks[@]}";
do
    for i in $(seq 1 $repetitions);
    do
        python3 pso.py ./images/$benchmark.png pso.$benchmark.$i $k $n $maxit $omega $alphaone $alphatwo $eps &
    done
    python3 kmeans.py ./images/$benchmark.png kmeans.$benchmark $k &
done

