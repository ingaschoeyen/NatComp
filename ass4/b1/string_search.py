
import random
import sys
from matplotlib import pyplot as plt


K = 2 # Number of candidates to sample at random for the tournament selection
ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "
GOAL_STRING = "Bonjour bitches"
CROSS_P : float = 1. # [0, 1] Probability of a crossover
LENGTH = len(GOAL_STRING)
MUT_RATE : float = 3/LENGTH # [0, 1] Rate of mutation for children
N = 200 # Population size
MAX_GENS = 100 # Maximum number of generations of one run
REPETITIONS = 10 # Number of runs
DIV_SUBSAMPLE_Q = 0.6 # [0, 1] Fraction of population to use to calculate diversity, lower to speed up


# Fraction of correct characters
def fitness(candidate : str, goal_string : str = GOAL_STRING):
    assert(len(candidate) == len(goal_string))

    correct = 0
    for i in range(len(candidate)):
        correct += 1 if candidate[i] == goal_string[i] else 0

    return correct / len(candidate)


def crossover(parent1 : str, parent2 : str):
    assert(len(parent1) == len(parent2))

    cutoff = random.randint(0, len(parent1) - 1)
    return parent1[:cutoff] + parent2[cutoff:], parent2[:cutoff] + parent1[cutoff:]


def mutate(sequence : str, mut_rate : float = MUT_RATE, alphabet : str = ALPHABET):
    return ''.join([random.choice(alphabet) if random.random() < mut_rate else c for c in sequence])


def init_pool(pop_size : int = N, str_len : int = LENGTH, alphabet : str = ALPHABET):
    return [''.join(random.choices(alphabet, k=str_len)) for _ in range(pop_size)]


def best(population : list[str], fitnesses : list[float]):
    best_ind = 0
    best_val = fitnesses[0]
    for i in range(len(population)):
        if fitnesses[i] > best_val:
            best_ind, best_val = i, fitnesses[i]
    return population[best_ind]


def ham_dist(str1 : str, str2 : str):
    assert(len(str1) == len(str2))
    return sum([1 if c1 != c2 else 0 for c1, c2 in zip(str1, str2)])


# Average of hamming distance between all pairs of strings in the given population
# Subsample quocient decides what percentage of population should be used for the diversity measure
def diversity(population : list[str], subsample_q : float = DIV_SUBSAMPLE_Q):
    population = random.sample(population, k=int(subsample_q * len(population)))

    ham_sum, pairs = 0, 0
    for i in range(len(population) - 1):
        for j in range(i + 1, len(population)):
            ham_sum += ham_dist(population[i], population[j])
            pairs += 1
    return ham_sum / pairs if pairs != 0 else 0.


# Sample parents from population using tournament selection
def tournament_selection(population : list[str], k : int = K):
    parents = []
    for _ in range(len(population)):
        rand_ids = random.sample(range(len(population)), k)
        candidates = [population[i] for i in rand_ids]
        cand_fits = [fitness(x) for x in candidates]
        parents.append(best(candidates, cand_fits))
    return parents


# Pair up and produce offspring
def new_generation(parents: list[str]):
    new_gen = []
    for i in range(0, len(parents), 2):
        child1, child2 = crossover(parents[i], parents[i+1])
        new_gen.extend([mutate(child1), mutate(child2)])
    return new_gen


# Run once with set parameters
# Return final generation, fitnesses of best candidates, and diversity
def repetition(max_gens : int = MAX_GENS, goal_string : str = GOAL_STRING):
    population = init_pool()
    # print("Initial population:\n", population)
    fitnesses = [fitness(x) for x in population]
    # print("Initial fitnesses:\n", fitnesses)
    best_sol = best(population, fitnesses)
    # print("Best candidate initially:", best_sol)
    # print("Best candidate fitness initially:", fitness(best_sol))
    best_fitnesses = [fitness(best_sol)]
    diversities = [diversity(population)]

    generation = 1
    while generation < max_gens and best_sol != goal_string:
        generation += 1

        # print("Population:\n", population)
        # print("Fitnesses:\n", fitnesses)
        # print("Best candidate:", best_sol)

        parents = tournament_selection(population)
        population = new_generation(parents)

        fitnesses = [fitness(x) for x in population]
        best_sol = best(population, fitnesses)
        best_fitnesses.append(fitness(best_sol))
        diversities.append(diversity(population))

    print("Best in last generation:", best_sol)
    print("Fitness:", fitness(best_sol))
    print("Generations:", generation)

    return generation, best_fitnesses, diversities


def plot_fitness(results : list[list[float]], output_path : str,
                 n : int = N, k : int = K, max_gens : int = MAX_GENS,
                 cross_p : float = CROSS_P, mut_rate : float = MUT_RATE):
    fig, ax = plt.subplots()
    ax.set_xlim([1, max_gens])
    ax.set_ylim([0, 1])
    for rep in results:
        plt.plot([i for i in range(max_gens)], rep + [rep[-1] for _ in range(max_gens - len(rep))])
    plt.xlabel("Generation")
    plt.ylabel("Fitness of best string")
    plt.title("Fitness development")

    textstr = '\n'.join((
    r'n = %d' % (n, ),
    r'k = %d' % (k, ),
    r'cross p = %.2f' % (cross_p, ),
    r'mutation rate: %.2f' % (mut_rate, )))

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # place a text box in lower right in axes coords
    ax.text(0.60, 0.25, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    plt.savefig(output_path)


def plot_diversity(results : list[list[float]], output_path : str,
                   n : int = N, k : int = K, max_gens : int = MAX_GENS, str_len : int = LENGTH,
                   cross_p : float = CROSS_P, mut_rate : float = MUT_RATE, subsample_r : float = DIV_SUBSAMPLE_Q):
    fig, ax = plt.subplots()
    ax.set_xlim([1, max_gens])
    ax.set_ylim([-0.5, str_len + 1])
    for rep in results:
        plt.plot([i for i in range(len(rep))], rep)
    plt.xlabel("Generation")
    plt.ylabel("Diversity")
    plt.title("Diversity development")

    textstr = '\n'.join((
    r'n = %d' % (n, ),
    r'k = %d' % (k, ),
    r'cross p = %.2f' % (cross_p, ),
    r'mutation rate: %.2f' % (mut_rate, ),
    r'subsample ratio: %.2f' % (subsample_r, )))

    # these are matplotlib.patch.Patch properties
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

    # place a text box in lower right in axes coords
    ax.text(0.55, 0.30, textstr, transform=ax.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)

    plt.savefig(output_path)


def plot_generations(generations : list[int], output_path : str,
                     max_gens : int = MAX_GENS):
    fig, ax = plt.subplots()
    ax.hist(generations)
    ax = plt.gca()
    ax.set_xlim([0, max_gens + 1])
    # ax.set_ylim([0, len(generations)])
    plt.locator_params(axis="both", integer=True, tight=True) # display only whole numbers on Y
    plt.xlabel("Generations")
    plt.ylabel("Amount of runs")
    plt.title("Last generation histogram")

    plt.savefig(output_path)


if __name__ == "__main__":
    generations = []
    results = []
    diversities = []
    for j in range(REPETITIONS):
        gen, best_fits, diverse = repetition()
        generations.append(gen)
        results.append(best_fits)
        diversities.append(diverse)

    print(generations)

    plot_generations(generations, "gens.png")
    plot_fitness(results, "fitness.png")
    plot_diversity(diversities, "diversity.png")
