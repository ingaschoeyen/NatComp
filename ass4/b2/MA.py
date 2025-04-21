
from EA import EA, read_dataset, plot_results, setup
import os
import sys
import numpy as np
import json
import time
class MA(EA):
    """
    This class implements the MA (Memetic Algorithm) algorithm.
    """

    def __init__(self, distance_matrix, population_size=100, mutation_rate=0.01, crossover_rate=0.7, tournament_size=2, elitism = 10, generations=100, horizon=15):
        super().__init__(distance_matrix, population_size, mutation_rate, crossover_rate, tournament_size, elitism, generations)

    # def local_search(self):
        """
        This function implements a local search algorithm.
        It uses a 2-opt algorithm to improve the route.
        """
        for n, instance in enumerate(self.population):
            route = instance[0]
            best_distance = instance[1]
            improved = True
            its = 0
            # greedy algo, so breaks on first improvement - while bc of double loop
            while improved and its < self.n:
                for i in range(len(route) - 1):
                    for j in range(i + 1, len(route)):
                        new_route = route[:]
                        new_route[i:j] = list(reversed(new_route[i:j]))[:]
                        new_distance = self.calculate_distance(new_route)
                        if new_distance < best_distance:
                            self.population[n] = (new_route, new_distance)
                            improved = False
                    its += 1
    
    def diff_distance(self, route, i, j):
        """
        This function calculates the difference in distance between two routes.
        It uses the 2-opt algorithm to calculate the distance.
        """
        # calculate the difference between the two segments that are switched
        # in the route
        # i and j are the indices of the two segments
        # that are switched
        # dist 1 = norm(diff(i, i-1)) + norm(diff(j, j-1))
        # dist 2 = norm(diff(i-1, j-1)) + norm(diff(i, j))
        # delta_dist = dist2 - dist1


        # def dist(city1, city2):
        #     return np.linalg.norm(np.array(city1) - np.array(city2))

        # dist1 = dist(self.cities[route[i]], self.cities[route[i-1]]) + dist(self.cities[route[j%len(route)]], self.cities[route[j-1]])
        # dist2 = dist(self.cities[route[i-1]], self.cities[route[j-1]]) + dist(self.cities[route[i]], self.cities[route[j%len(route)]])
        dist1 = self.distance_matrix[route[i], route[i-1]] + self.distance_matrix[route[j%len(route)], route[j-1]]
        dist2 = self.distance_matrix[route[i-1], route[j-1]] + self.distance_matrix[route[i], route[j%len(route)]]
        delta_dist = dist2 - dist1
  
        return delta_dist


    def quick_local_search(self):
        """
        This function implements a quick local search algorithm.
        It uses a 2-opt algorithm to improve the route.
        """
        for n, instance in enumerate(self.population):
            route = instance[0]
            improved = False
            # greedy algo, so breaks on first improvement - while bc of double loop
            while not improved:
                for i in range(len(route) - 1):
                    for j in range(i + 1, len(route)):
                        delta_dist = self.diff_distance(route, i, j)
                        if delta_dist < 0:
                            new_route = route[:]
                            new_route[i:j] = list(reversed(new_route[i:j]))[:]
                            new_distance = self.calculate_distance(new_route)
                            self.population[n] = (new_route, new_distance)
                            improved = True
                            break
                    if improved:
                        break

            if improved:
                break



    def do_a_memetic(self, early_stopping=False):
        """
        This function implements the memetic algorithm.
        It uses a local search to improve the solutions.
        """

        for _ in range(self.max_generations):
            self.quick_local_search()
            self.evaluate_population()
            self.update_population()
            self.generation += 1
            if self.generation % 10 == 0:
                print(f"Generation {self.generation}: Best Distance: {self.best_distance}")
            if self.generation > 50 and np.mean(self.best_distances) == self.best_distance:
                print(f"Stopping criteria met at generation {self.generation}")
                break

            if early_stopping and self.best_distance < 0.5*self.init_distance:
                print(f"Stopping criteria met at generation {self.generation}")
                break

        return self.best_route, self.best_distance


if __name__ == "__main__":
    distance_matrix, population_size, mutation_rate, crossover_rate, generations, n_runs = setup()

    final_distances, best_distances, mean_distances, var_distances, cpu_times = [], [], [], [], []

    for i in range(n_runs):
        print(f"Starting Run {i+1}...")
        time_init = time.time()
        ma = MA(distance_matrix, population_size, mutation_rate, crossover_rate, generations=generations)
        best_route, best_distance = ma.do_a_memetic(early_stopping=True)
        
        time_end = time.time()  
        cpu_times.append(time_end - time_init)
        print(f"Run {i+1} Time: {cpu_times[-1]} seconds")
        
        final_distances.append(best_distance)
        best_distances.append(ma.best_distance)
        mean_distances.append(ma.distances_mean)
        var_distances.append(ma.distances_var)

        print(f"Best Distance Run {i+1}: {best_distance}")

            # return the best distance, mean distance and variance, mean convergence time and variance,


    results = {
        "final_distances": final_distances,
        "mean_distances": np.mean(final_distances),
        "var_distances": np.var(final_distances),
        "mean_convergence_time": np.mean(len(best_distances)),
        "cpu_time": np.mean(cpu_times),
    }

    # write results to file
    dataset = sys.argv[1]
    with open(f"results_MA_{dataset}_{population_size}_{mutation_rate}_{crossover_rate}.json", "w") as f:
        # write the results in json format
        json.dump(results, f, indent=4)
    print(f"Results saved to results_MA_{dataset}_{population_size}_{mutation_rate}_{crossover_rate}_early_Stopping.json")



    plot_results(best_distances, mean_distances, var_distances, algo_type="MA")