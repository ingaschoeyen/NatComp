from EA import EA, setup
from MA import MA
import time
import numpy as np

## This script compares the EA and MA algorithms on the TSP problem.
## It runs each algorithm until a specified threshold is reached in fitness


def simulation_EA(cities, population_size, mutation_rate, crossover_rate, generations, n_runs):
    """
    This function runs the EA simulation.
    It returns the best distance and the mean distance for each run.
    """
    final_distances, best_distances, mean_distances, var_distances, cpu_times = [], [], [], [], []

    for i in range(n_runs):
        print(f"Starting Run {i+1}...")
        time_init = time.time()
        ea = EA(cities, population_size, mutation_rate, crossover_rate, generations)
        _, best_distance = ea.do_a_ea()
        
        time_end = time.time()  
        cpu_times.append(time_end - time_init)
        print(f"Run {i+1} Time: {cpu_times[-1]} seconds")
        
        final_distances.append(best_distance)
        best_distances.append(ea.best_distance)
    
    return final_distances, best_distances, mean_distances, var_distances, cpu_times

def plot_comparison():
    pass




if __name__ == "__main__":

    # initialise setup
    cities, population_size, mutation_rate, crossover_rate, generations, n_runs = setup()
    
    n_runs = 10

    # setup parallel cpu

    # run parallel EA
    # final_distances_ea, best_distances_ea, mean_distances_ea, var_distances_ea, cpu_times_ea = simulation_EA(cities, population_size, mutation_rate, crossover_rate, generations, n_runs)
        

    # loop over n_runs of EA
    final_distances_ea, best_distances_ea, mean_distances_ea, var_distances_ea, cpu_times_ea = [], [], [], [], []
    for i in range(n_runs):
        print(f"Starting Run {i+1}...")
        time_init = time.time()
        ea = EA(cities, population_size, mutation_rate, crossover_rate, generations)
        best_route, best_distance = ea.do_a_ea(threshold=0.2)
        
        time_end = time.time()  
        cpu_times_ea.append(time_end - time_init)
        print(f"Run {i+1} Time: {cpu_times_ea[-1]} seconds")
        
        final_distances_ea.append(best_distance)
        best_distances_ea.append(ea.best_distance)
        mean_distances_ea.append(np.mean(ea.distances_mean))
        var_distances_ea.append(np.var(ea.distances_var))

    # run parallel MA
    # final_distances_ma, best_distances_ma, mean_distances_ma, var_distances_ma, cpu_times_ma = simulation_MA(cities, population_size, mutation_rate, crossover_rate, generations, n_runs)

    # loop over n_runs of MA
    final_distances_ma, best_distances_ma, mean_distances_ma, var_distances_ma, cpu_times_ma = [], [], [], [], []
    for i in range(n_runs):
        print(f"Starting Run {i+1}...")
        time_init = time.time()
        ma = MA(cities, None, population_size, mutation_rate, crossover_rate, generations)
        best_route, best_distance = ma.do_a_memetic()
        
        time_end = time.time()  
        cpu_times_ma.append(time_end - time_init)
        print(f"Run {i+1} Time: {cpu_times_ma[-1]} seconds")
        
        final_distances_ma.append(best_distance)
        best_distances_ma.append(ma.best_distance)
        mean_distances_ma.append(np.mean(ma.distances_mean))
        var_distances_ma.append(np.var(ma.distances_var))   

    
    # get averages of runs and variance


    # plot results
    plot_comparison()