#!/bin/bash
# Usage: ./run.sh [N] [cohesion] [separation] [alignment]
N=100
max=16
for i in $(seq 1 $max)
do
    for j in $(seq 1 $max)
    do
        for k in $(seq 1 $max)
        do
            echo "Running simulation with N=$N, cohesion=$i, separation=$j, alignment=$k"
            node boids_grid.mjs $N $i $j $k $max
        done
    done
done
# usage ./grid_search.sh 
python grid_search.py $N $max