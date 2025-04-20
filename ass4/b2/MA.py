
from EA import EA, read_dataset, plot_results, setup
import os
import sys
import numpy as np
import time
class MA(EA):
    """
    This class implements the MA (Memetic Algorithm) algorithm.
    """

    def __init__(self, cities, permutations, population_size=100, mutation_rate=0.01, crossover_rate=0.7, tournament_size=2, elitism = 10, generations=1000, horizon=15):
        super().__init__(cities, permutations, population_size, mutation_rate, crossover_rate, tournament_size, elitism, generations)

    def local_search(self):
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
        dist = - np.linalg.norm(np.array(self.cities[route[i]]) - np.array(self.cities[route[i + 1]])) - np.linalg.norm(np.array(self.cities[route[j]]) - np.array(self.cities[route[j+1]])) + np.linalg.norm(np.array(self.cities[route[i+1]]) - np.array(self.cities[route[j+1]])) + np.linalg.norm(np.array(self.cities[route[i]]) - np.array(self.cities[route[j]]))
        print(f"Diff Distance: {dist}")
        return dist


    def quick_local_search(self):
        """
        This function implements a quick local search algorithm.
        It uses a 2-opt algorithm to improve the route.
        """
        for n, instance in enumerate(self.population):
            route = instance[0]
            best_distance = instance[1]
            improved = True
            its = 0
            # greedy algo, so breaks on first improvement - while bc of double loop
            while improved:
                for i in range(len(route) - 1):
                    for j in range(i + 1, len(route)):
                        delta_dist = self.diff_distance(route, i, j)
                        if delta_dist < 0:
                            new_route = route[:]
                            new_route[i:j] = list(reversed(new_route[i:j]))[:]
                            new_distance = best_distance + delta_dist
                            self.population[n] = (new_route, new_distance)
                            improved = False

    def do_a_memetic(self):
        """
        This function implements the memetic algorithm.
        It uses a local search to improve the solutions.
        """

        for _ in range(self.max_generations):
            self.quick_local_search()
            self.evaluate_population()
            self.update_population()
            self.generation += 1
            print(f"Generation {self.generation}: Best Distance: {self.best_distance}")


        return self.best_route, self.best_distance


if __name__ == "__main__":
    cities, population_size, mutation_rate, crossover_rate, generations, n_runs = setup()
    permutations = None

    final_distances, best_distances, mean_distances, var_distances, cpu_times = [], [], [], [], []

    for i in range(n_runs):
        print(f"Starting Run {i+1}...")
        time_init = time.time()
        ma = MA(cities, permutations, population_size, mutation_rate, crossover_rate, generations)
        best_route, best_distance = ma.do_a_memetic()
        
        time_end = time.time()  
        cpu_times.append(time_end - time_init)
        print(f"Run {i+1} Time: {cpu_times[-1]} seconds")
        
        final_distances.append(best_distance)
        best_distances.append(ma.best_distance)
        mean_distances.append(np.mean(ma.distances_mean))
        var_distances.append(np.var(ma.distances_var))

        print(f"Best Distance Run {i+1}: {best_distance}")


    plot_results(final_distances, best_distances, mean_distances, var_distances)