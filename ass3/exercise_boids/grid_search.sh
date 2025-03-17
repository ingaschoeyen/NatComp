#!/bin/bash
# Usage: ./run.sh [N] [cohesion] [separation] [alignment]
N=100
max=9
inner=10
outer=50
for i in $(seq 1 $max)
do
    for j in $(seq 1 $max)
    do
        for k in $(seq 1 $max)
        do
            echo "Running simulation with N=$N, cohesion=$i, separation=$j, alignment=$k"
            node boids_grid.mjs $N $i $j $k $max $inner $outer  
        done 
    done
done
# usage ./grid_search.sh 
python grid_search.py $N $max $inner $outer