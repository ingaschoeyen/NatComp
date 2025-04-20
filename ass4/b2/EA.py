# EA.py

import matplotlib.pyplot as plt
import random
import sys
import numpy as np
import os
import time
import json
# sys arg structure
# python EA.py <dataset_file_name> <population_size> <mutation_rate> <crossover_rate> <generations>


class EA:


    def __init__(self, cities, permutations, population_size=100, mutation_rate=0.01, crossover_rate=0.7, tournament_size=2, elitism = 10, generations=1000, horizon=15):
        self.cities = cities # list of coordinates of cities [N x 2]
        self.n = len(cities)
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.tournament_size = tournament_size
        self.elitism = elitism
        self.max_generations = generations
        self.conv_horiz = horizon # number of generations to check for convergence
        if permutations is None:
            self.population = self.create_population2()
        else:
            self.population = self.create_population(permutations) # list of tuples (route, distance)
        self.best_route = None
        self.best_distance = float('inf')
        self.best_distances = [] # to track best distance
        self.distances_mean = [] # to track mean distance
        self.distances_var = [] # to track variance in distances
        self.generation = 0  
        print("Initiated")

    def create_population(self, permutations):
        population = []
        # sample random indices from permutations
        routes = random.sample(list(permutations), self.population_size)
        for route in routes:
            distance = self.calculate_distance(route)
            population.append((route, distance))
        return population
    
    def create_population2(self):
        population = []
        for _ in range(self.population_size):
            # create a random route
            route = np.random.permutation(range(self.n))
            distance = self.calculate_distance(route)
            population.append((route, distance))
        return population
    
    def calculate_distance(self, route):
        distance = 0
        for i in range(len(route)-1):
            city1 = self.cities[route[i]]
            city2 = self.cities[route[i+1]]
            distance += np.linalg.norm(np.array(city1) - np.array(city2))
        return distance
    

    def crossover(self, parent1, parent2):
        # order crossover
        start, end = sorted(random.sample(range(self.n), 2))
        child1 = [-1] * self.n
        child2 = [-1] * self.n
        child1[start:end] = parent1[start:end]
        child2[start:end] = parent2[start:end]
        self.fill_child(child1, parent2)
        self.fill_child(child2, parent1)
        return child1, child2

    def fill_child(self, child, parent2):
        # fill the child with the remaining genes from other parent
        prt_idx = 0
        for i in range(self.n):
            if child[i] == -1:
                while parent2[prt_idx] in child:
                    prt_idx += 1
                child[i] = parent2[prt_idx]
        return child
    
    def mutate(self, route):
        # swap mutation
        # select two random indices
        idx1, idx2 = random.sample(range(self.n), 2)
        # swap the two cities
        route[idx1], route[idx2] = route[idx2], route[idx1]
        return route

    
    def evaluate_population(self):
        # sort the population by distance, lowest distance first
        self.population.sort(key=lambda x: x[1])
        # update the best route and distance
        best_solution = self.population[0]
        self.best_distance = best_solution[1]
        self.best_route = best_solution[0]
        # update the best distances
        self.best_distances.append(self.best_distance)
        # update the mean and variance of the distances
        self.distances_mean.append(np.mean([d[1] for d in self.population]))
        self.distances_var.append(np.var([d[1] for d in self.population]))




    def tournament_selection(self):
        try:
            tournament = random.sample(self.population, k = self.tournament_size)
        except ValueError:
            print("Tournament size is larger than population size. Adjusting tournament size.")
        tournament.sort(key=lambda x: x[1])
        return tournament[0][0], tournament[0][1]

    def update_population(self):
        # elitism - keep the best individuals
        if self.elitism == 0:
            new_population = []
        else:
            new_population = self.population[:self.elitism]
        for i in range(self.population_size//2):
            # select three parents for crossover + mutation
            parent1, dist1 = self.tournament_selection()
            parent2, dist2 = self.tournament_selection()
            if random.random() < self.crossover_rate:
                offspring1, offspring2 = self.crossover(parent1, parent2)
                new_population.append((offspring1, self.calculate_distance(offspring1)))
                new_population.append((offspring2, self.calculate_distance(offspring2)))
            # if crossover is not performed, add the parents to the new population
            else:
                new_population.append((parent1, dist1))
                new_population.append((parent2, dist2))
        # mutate the offspring
        for k in range(self.population_size):
            if random.random() < self.mutation_rate:
                offspring3 = self.mutate(new_population[k][0])
                new_population[k] = (offspring3, self.calculate_distance(offspring3))
        # if the new population is larger than the population size, truncate it to the population size
        if len(new_population) > self.population_size:
            new_population = new_population[:self.population_size]
        self.population = new_population



    def do_an_evolution(self):
        for _ in range(self.max_generations):
            self.evaluate_population()
            # print(f"Generation: {self.generation}, Best Distance: {self.best_distance}")
            self.update_population()
            self.generation += 1    
            if self.generation > 50 and np.mean(self.best_distances[-self.conv_horiz:]) == self.best_distance:
                print("Converged")
                break
        return self.best_route, self.best_distance
    



# function to read dataset from file    
def read_dataset(file_path):
    cities = []
    # read the file and extract the coordinates of the cities
    with open(file_path, 'r') as f:
        # check if 2 columns or three
        lines = f.readlines()
        if len(lines[0].split()) == 3:
            print("3 columns")
            for line in lines:
                x, y = map(float, line.strip().split()[1:])
                cities.append((x, y))
        elif len(lines[0].split()) == 2:
            print("2 columns")
            for line in lines:
                x, y = map(float, line.strip().split())
                cities.append((x, y))
        else:
            raise ValueError("Invalid file format. Please check the dataset file. Expected 2 or 3 columns.")
    return cities

def plot_results(final_dists, best_distances, mean_distances, var_distances, algo_type="EA"):
    

    # plot the best distance
    plt.figure(figsize=(12, 6))
    for i in range(len(best_distances)):
            # compute stddev intervals
        # std_lower = [x-y for x, y in zip(mean_distances[i], var_distances[i])]
        std_upper = [x+np.sqrt(y) for x, y in zip(mean_distances[i], var_distances[i])]
    
        
        # plot the mean distance
        plt.plot(mean_distances[i], label=f"Mean Distance {i+1}")
        plt.plot(best_distances[i], label=f"Best Distance {i+1}")
        # plot the variance distance as shaded area
        plt.fill_between(range(len(var_distances[i])), mean_distances[i], std_upper, alpha=0.2)
       
     # configure runs plot   
    plt.xlabel("Generation")
    plt.ylabel("Distance")
    plt.suptitle("Best Distance vs Generation")
    plt.legend()
    plt.title(f"N = {population_size}, mu = {mutation_rate}, pc = {crossover_rate}")

    dataset = sys.argv[1]
    fig_name = f"best_distance_{algo_type}_{dataset}_{population_size}_{mutation_rate}_{crossover_rate}.png"

    plt.savefig(fig_name)
    plt.show()


def setup():
    dataset = sys.argv[1]
    if len(sys.argv) < 3:    
        population_size = 100
        mutation_rate = 0.1
        crossover_rate = 0.7
        generations = 100
        n_runs = 10
    else:
        population_size = int(sys.argv[2])
        mutation_rate = float(sys.argv[3])
        crossover_rate = float(sys.argv[4])
        generations = int(sys.argv[5])
        n_runs = int(sys.argv[6])


    file_loc = f"/datasets/{dataset}.txt"
    file_path = os.path.dirname(__file__) + file_loc
    cities = read_dataset(file_path)
    
    return cities, population_size, mutation_rate, crossover_rate, generations, n_runs

if __name__ == "__main__":
    
    # setup
    cities, population_size, mutation_rate, crossover_rate, generations, n_runs = setup()
    
    
    # create a list of permutations of the cities
    perms = None

    final_distances = []
    best_distances = []
    mean_distances = []
    var_distances = []
    times = []
    # repeat the search 10 times
    for i in range(n_runs):
        print(f"Starting Run {i+1} of 10")
        time_init = time.time()
        # initiate the algorithm
        ea = EA(cities, perms, population_size, mutation_rate, crossover_rate, generations=generations)
        
        # run the search, get the best route and distance
        best_route, best_distance = ea.do_an_evolution()

        time_end = time.time()
        times.append(time_end - time_init)
        print(f"Time taken: {time_end - time_init} seconds")

        # save the results for plotting
        final_distances.append(best_distance)
        best_distances.append(ea.best_distances)
        mean_distances.append(ea.distances_mean)
        var_distances.append(ea.distances_var)
        
        
        # print the best route and distance
        print(f"Run {i+1}:")
        print(f"Best Distance: {best_distance}")



    # return the best distance, mean distance and variance, mean convergence time and variance,
    #  cpu time and memroy usage as dictionary
    results = {
        "final_distances": final_distances,
        "mean_distances": np.mean(final_distances),
        "var_distances": np.var(final_distances),
        "mean_convergence_time": np.mean(len(best_distances)),
        "cpu_time": np.mean(times),
    }

    # write results to file
    dataset = sys.argv[1]
    with open(f"results_EA_{dataset}_{population_size}_{mutation_rate}_{crossover_rate}.json", "w") as f:
        # write the results in json format
        json.dump(results, f, indent=4)
    print(f"Results saved to results_EA_{dataset}_{population_size}_{mutation_rate}_{crossover_rate}.json")


    # plot the results
    plot_results(final_distances, best_distances, mean_distances, var_distances)

