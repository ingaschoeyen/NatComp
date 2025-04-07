
import random
import sys
from matplotlib import pyplot as plt


MAX_GENS : int = 1500
LENGTH : int = 100
MUT_RATE : float = 1/LENGTH
REPETITIONS : int = 5

def fitness(bitstring : int):
    result = 0
    while bitstring > 0:
        result += bitstring % 2
        bitstring //= 2
    return result

def mutate(bitstring : int, prob : float = MUT_RATE):
    result = 0
    for _ in range(LENGTH):
        throw = random.random()
        if throw <= prob:
            result += 1 - bitstring % 2
        else:
            result += bitstring % 2
        result *= 2
        bitstring //= 2
    return result // 2

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
    results = []
    for rep in range(REPETITIONS):
        x = random.getrandbits(LENGTH)
        x_fit = fitness(x)
        best_fit = x_fit

        print("{0:b}".format(x))
        print("Init fitness: ", x_fit)

        fitnesses = [x_fit]
        fitnesses2 = [best_fit]
        max_fitness_it = 1

        for it in range(MAX_GENS):
            x_mut = mutate(x)
            x_mut_fit = fitness(x_mut)

            # print("{0} : {1:b}".format(it, x_mut))
            # print("fitness: ", x_mut_fit)

            best_fit = max(best_fit, x_mut_fit) # with if condition, is same as current fitness

            if x_mut_fit > x_fit:
                x = x_mut
                x_fit = x_mut_fit
                max_fitness_it = it # not the best iteration without the if condition

            fitnesses.append(best_fit)
        results.append(fitnesses)

    output_path = sys.argv[1] if len(sys.argv) > 1 else "result.png"

    plot_fitness(results, output_path)
    # print(fitnesses)
    print("Best fitness achieved at iteration", max_fitness_it)


