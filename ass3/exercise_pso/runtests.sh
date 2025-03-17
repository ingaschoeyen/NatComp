#!/bin/bash

# run as: bash runtests.sh <k> <n> <maxit> <omega> <alphaone> <alphatwo>

# names of files from /images/ on which to run the tests on
# declare -a benchmarks=("airplane" "peppers" "lenna" "mandril")
declare -a benchmarks=("airplane" "peppers" "lenna" "mandril")

k=$1
n=$2
maxit=$3
omega=$4
alphaone=$5
alphatwo=$6
eps=0 # can be used to get result of set quality in less iterations

# how many times to compute the pso for each benchmark (kmeans always calculated only once)
repetitions=5

# runs all benchmarks simultaneously in the background
for benchmark in "${benchmarks[@]}";
do
    for i in $(seq 1 $repetitions);
    do
        python3 pso.py ./images/$benchmark.png pso.$benchmark.$i $k $n $maxit $omega $alphaone $alphatwo $eps &
    done
    python3 kmeans.py ./images/$benchmark.png kmeans.$benchmark $k &
done

