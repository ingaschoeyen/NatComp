from EA import EA, setup, plot_results
from MA import MA
import time
import numpy as np
import matplotlib.pyplot as plt
import sys
import json

## This script compares the EA and MA algorithms on the TSP problem.
## It runs each algorithm until a specified threshold is reached in fitness


def plot_comparison_2(results):
    # plot histogram 
    plt.figure(figsize=(10, 5))

    for key, value in results.items():
        plt.bar(key, value["mean_final_distance"], yerr=value["var_final_distance"], label=key)
        plt.bar(key, value["mean_cpu_time"], yerr=value["var_cpu_time"], label=key + " CPU Time", alpha=0.5)
    plt.title("Comparison of EA and MA")




if __name__ == "__main__":

    # initialise setup
    distance_matrix, population_size, mutation_rate, crossover_rate, generations, n_runs = setup()
    # loop over n_runs of EA 
    n_runs = 10
    final_distances_ea, convergence_time_ea, best_distances_ea, mean_distances_ea, var_distances_ea, cpu_times_ea = [], [], [], [], [], []
    for i in range(n_runs):
       

       
        print(f"Starting EA Run {i+1}...")
        time_init = time.time()
        ea = EA(distance_matrix, population_size, mutation_rate, crossover_rate, generations)
        best_route, best_distance = ea.do_an_evolution()
        
        time_end = time.time()  
        cpu_times_ea.append(time_end - time_init)
        print(f"Run {i+1} Time: {cpu_times_ea[-1]} seconds")
        
        final_distances_ea.append(best_distance)
        best_distances_ea.append(ea.best_distance)
        convergence_time_ea.append(ea.generation)
        mean_distances_ea.append(ea.distances_mean)
        var_distances_ea.append(ea.distances_var)

    plot_results(best_distances_ea, mean_distances_ea, var_distances_ea, algo_type="EA_exp2")
    # loop over n_runs of MA
    final_distances_ma, convergence_time_ma, best_distances_ma, mean_distances_ma, var_distances_ma, cpu_times_ma = [], [], [], [], [], []
    for i in range(n_runs):
        print(f"Starting MA Run {i+1}...")
        time_init = time.time()
        ma = MA(distance_matrix, population_size, mutation_rate, crossover_rate, generations)
        best_route, best_distance = ma.do_a_memetic(early_stopping=True)
        
        time_end = time.time()  
        cpu_times_ma.append(time_end - time_init)
        print(f"Run {i+1} Time: {cpu_times_ma[-1]} seconds")
    
        final_distances_ma.append(best_distance)
        convergence_time_ma.append(len(ma.best_distances))
        best_distances_ma.append(ma.best_distance)
        mean_distances_ma.append(ma.distances_mean)
        var_distances_ma.append(ma.distances_var)

    plot_results(best_distances_ma, mean_distances_ma, var_distances_ma, algo_type="MA_exp2")

    
    # get averages of runs and variance
    mean_final_distances_ea = np.mean(final_distances_ea)
    mean_final_distances_ma = np.mean(final_distances_ma)
    var_final_distances_ea = np.var(final_distances_ea)
    var_final_distances_ma = np.var(final_distances_ma)

    mean_cpu_time_ea = np.mean(cpu_times_ea)
    mean_cpu_time_ma = np.mean(cpu_times_ma)
    var_cpu_time_ea = np.var(cpu_times_ea)
    var_cpu_time_ma = np.var(cpu_times_ma)

    results = {
        "EA": {
            "mean_final_distance": mean_final_distances_ea,
            "var_final_distance": var_final_distances_ea,
            "mean_cpu_time": mean_cpu_time_ea,
            "var_cpu_time": var_cpu_time_ea,
            "convergence_time": np.mean(convergence_time_ea)
        },
        "MA": {
            "mean_final_distance": mean_final_distances_ma,
            "var_final_distance": var_final_distances_ma,
            "mean_cpu_time": mean_cpu_time_ma,
            "var_cpu_time": var_cpu_time_ma,
            "convergence_time": np.mean(convergence_time_ma)
        }
    }

    # dump the results to json file
    dataset = sys.argv[1]
    with open(f"results_comparison_{dataset}_{population_size}_{mutation_rate}_{crossover_rate}_exp2.json", "w") as f:
        # write the results in json format
        json.dump(results, f, indent=4)

    # plot results
    plot_comparison_2(results)