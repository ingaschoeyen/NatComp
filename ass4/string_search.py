
import random
import sys
from matplotlib import pyplot as plt


K = 2
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
GOAL_STRING = "Bonjour bitches"
CROSS_P : float = 1
LENGTH = len(GOAL_STRING)
# MUT_RATE : float = 1/LENGTH
MUT_RATE : float = 0
# MUT_RATE : float = 3/LENGTH
N = 200
MAX_GENS = 100


# Fraction of correct characters
def fitness(candidate : str):
    assert(len(candidate) == LENGTH)

    correct = 0
    for i in range(LENGTH):
        correct += 1 if candidate[i] == GOAL_STRING[i] else 0

    return correct / LENGTH


def crossover(parent1 : str, parent2 : str):
    assert(len(parent1) == len(parent2) == LENGTH)

    cutoff = random.randint(0, LENGTH - 1)
    return parent1[:cutoff] + parent2[cutoff:], parent2[:cutoff] + parent1[cutoff:]


def mutate(sequence : str):
    return ''.join([random.choice(ALPHABET) if random.random() < MUT_RATE else c for c in sequence])


def init_pool():
    return [''.join(random.choices(ALPHABET, k=LENGTH)) for _ in range(N)]


def best(population : list[str], fitnesses : list[float]):
    best_ind = 0
    best_val = fitnesses[0]
    for i in range(len(population)):
        if fitnesses[i] > best_val:
            best_ind, best_val = i, fitnesses[i]
    return population[best_ind]


# Sample parents from population using tournament selection
def tournament_selection(population : list[str], k):
    parents = []
    for _ in range(len(population)):
        rand_ids = random.sample(range(N), k)
        candidates = [population[i] for i in rand_ids]
        cand_fits = [fitness(x) for x in candidates]
        parents.append(best(candidates, cand_fits))
    return parents


# Pair up and produce offspring
def new_generation(parents: list[str]):
    new_gen = []
    for i in range(0, N, 2):
        child1, child2 = crossover(parents[i], parents[i+1])
        new_gen.extend([mutate(child1), mutate(child2)])
    return new_gen


def plot_fitness(results : list[int], output_path : str):
    fig, ax = plt.subplots()
    ax = plt.gca()
    ax.set_xlim([1, MAX_GENS + 1])
    ax.set_ylim([0, LENGTH + 1])
    for rep in range(len(results)):
        plt.plot([i + 1 for i in range(len(results[rep]))], results[rep])
    plt.xlabel("Iteration")
    plt.ylabel("Fitness of bitstring x")
    plt.title("Without if condition")

    textstr = '\n'.join((
    r'generations: %d' % (MAX_GENS, ),
    r'length: %d' % (LENGTH, ),
    r'mutation rate: %.2f' % (MUT_RATE, )))

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # place a text box in lower right in axes coords
    ax.text(0.60, 0.2, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    plt.savefig(output_path)


if __name__ == "__main__":
    generations = []
    for j in range(10):
        population = init_pool()
        # print("Initial population:\n", population)
        fitnesses = [fitness(x) for x in population]
        # print("Initial fitnesses:\n", fitnesses)
        best_sol = best(population, fitnesses)
        # print("Best candidate initially:", best_sol)
        # print("Best candidate fitness initially:", fitness(best_sol))

        generation = 0
        while generation < MAX_GENS and best_sol != GOAL_STRING:
            # print("Population:\n", population)
            # print("Fitnesses:\n", fitnesses)
            # print("Best candidate:", best_sol)

            parents = tournament_selection(population, K)
            population = new_generation(parents)

            fitnesses = [fitness(x) for x in population]
            best_sol = best(population, fitnesses)

            generation += 1

        print("Best in last generation:", best_sol)
        print("Fitness:", fitness(best_sol))
        print("Generations:", generation)
        generations.append(generation)

    print(generations)
