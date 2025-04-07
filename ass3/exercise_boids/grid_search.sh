#!/bin/bash
# Usage: ./run.sh [N] [cohesion] [separation] [alignment]
N=100
max=9
inner=10
outer=100

declare -a c_values=$(seq 1 2)
declare -a s_values=$(seq 1 2)
declare -a a_values=$(seq 1 $max)

for i in $c_values
do
    for j in $s_values
    do
        for k in $a_values
        do
            echo "Running simulation with N=$N, cohesion=$i, separation=$j, alignment=$k"
            node boids_grid.mjs $N $i $j $k $max $inner $outer &  
        done 
    done
done
# usage ./grid_search.sh 
# python grid_search.py $N $max $inner $outer