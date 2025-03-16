#!/bin/bash
# Usage: ./run.sh [N] [cohesion] [separation] [alignment]
N=100

for i in {1..10}
do
    for j in {1..10}
    do
        for k in {1..10}
        do
            echo "Running simulation with N=$N, cohesion=$j, separation=$k, alignment=$l"
            javascript boids.js $N $i $j $k > boids_out/boids_N$N_C$i_S$j_A$k.txt 
            python boid_plots.py plots/boids_N$N_C$i_S$j_A$k
        done
    done
done
# usage ./grid_search.sh 
python grid_search.py $N 