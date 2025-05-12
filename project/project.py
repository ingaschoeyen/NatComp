import sys
import matplotlib.pyplot as plt
import numpy as np
import scipy


def generate_population_uniform(n: int, dimension: int = 2, low: int = -1, high: int = 1):
    return np.array([[np.random.uniform(low, high) for _ in range(dimension)] for _ in range(n)])

def generate_population_normal(n: int, dimension: int = 2, mu: float = 0, sigma: float = 1):
    return np.array([[np.random.normal(mu, sigma) for _ in range(dimension)] for _ in range(n)])

def distance_euclid(first, second):
    return np.linalg.norm(np.array(first) - np.array(second))

def candidate_distances(voter, candidates, dist_metric):
    return [dist_metric(voter, candidate) for candidate in candidates]

def closest_candidates(voters, candidates, dist_metric):
    return [np.argmin(candidate_distances(voter, candidates, dist_metric)) for voter in voters]

def instant_runoff(voters, candidates, dist_metric):
    vote_count = [0 for _ in range(len(candidates))]
    for favourite in closest_candidates(voters, candidates, dist_metric):
        vote_count[favourite] += 1

    return vote_count

def percentage_distribution(results):
    return scipy.softmax(results)

# Uses only first 2 dimensions of preferences
def plot_distribution(voters, candidates, output_path = "./res_dis.png"):
    plt.scatter(voters[:,0], voters[:,1], c=closest_candidates(voters, candidates, distance_euclid), alpha=1)
    plt.scatter(candidates[:,0], candidates[:,1], c=range(len(candidates)), s=[200 for _ in range(len(candidates))], alpha=0.5)
    plt.savefig(output_path)

def plot_histogram(results, output_path = "./res_hist.png"):
    fig, ax = plt.subplots()
    ax.hist(results)

    ax.set_xlim([0, max(results)])

    ax = plt.gca()
    plt.savefig(output_path)


if __name__ == "__main__":
    voters = generate_population_uniform(100, 2)
    cands = generate_population_uniform(10, 2)
    plot_distribution(voters, cands)
    plot_histogram(closest_candidates(voters, cands, distance_euclid))
