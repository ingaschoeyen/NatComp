#!/bin/bash
# Usage: ./run.sh [N] [cohesion] [separation] [alignment]
N=100
max=9
inner=10
outer=100

<<<<<<< HEAD
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
=======
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

>>>>>>> 76362d6aa83825d8512f62150e43ab354cd3dc43
