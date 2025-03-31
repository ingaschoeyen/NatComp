#!/bin/bash
# Usage: ./run.sh [N] [cohesion] [separation] [alignment]
N=100
max=9
inner=10
outer=100

# select the range of params to simulate asynchronyously
declare -a a_params=$(seq 1 1)
declare -a b_params=$(seq 1 1)
declare -a c_params=$(seq 1 1)

for i in $a_params;
do
    for j in $b_params;
    do
        for k in $c_params;
        do
            echo "Running simulation with N=$N, cohesion=$i, separation=$j, alignment=$k"
            node boids_grid.mjs $N $i $j $k $max $inner $outer &
        done
    done
done
# usage ./grid_search.sh
wait
# python3 grid_search.py $N $max $inner $outer

