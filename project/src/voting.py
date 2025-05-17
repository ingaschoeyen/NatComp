import numpy as np
import scipy
from geometry import *

class Population():

    def __init__(self):
        self.pop : list[Point] = [] # Population

    # Uniform distribution
    def init_uniform(self, n: int, dimension: int = 2, low: int = -1, high: int = 1):
        self.pop = np.array([[np.random.uniform(low, high) for _ in range(dimension)] for _ in range(n)])

    # Normal (Gaussian) distribution
    def init_normal(self, n: int, dimension: int = 2, mu: float = 0, sigma: float = 1):
        self.pop = np.array([[np.random.normal(mu, sigma) for _ in range(dimension)] for _ in range(n)])

    # TODO Update the population based on polls and/or previous results
    def update(self, polls):
        pass


# First past the post (Instant runoff/plurality)
# Every voter has one vote to cast
def fptp(voters : Population, candidates : Population, dist_metric = distance_euclid):
    vote_count = [0 for _ in range(len(candidates))]
    for favourite in closest_points(voters.pop, candidates.pop, dist_metric):
        vote_count[favourite] += 1

    return vote_count

# TODO Approval voting
# Every voter can approve of (vote for) any number of candidates
# Requires a threshold for deciding where the line between acceptable and non-acceptable candidate is
def approval(voters : Population, candidates : Population, threshold : float, dist_metric = distance_euclid):
    pass

# TODO (*Complete*) single transferable vote ranked choice voting
# Every voter ranks *all* candidates in order of preference
# If a preferred candidate is not selected, the vote is transfered to a lower ranked candidate
# Requires a threshold for selecting a candidate (percentage of all votes required)
# TODO can also use the Droop quota as threshold, requires number of mandates to distribute
# TODO incomplete stv - rank only a subset of candidates, lowers voting power of voters, requires threshold as in approval
def stv(voters : Population, candidates : Population, threshold : float = 0.05, dist_metric = distance_euclid):
    pass

# Softmax to create percentages from number of received votes
def percentage_distribution(results : list[int]):
    return scipy.softmax(results)

# TODO Voter satisfaction efficiency
def vse(voters : Population, candidates : Population, results : list[int], dist_metric = distance_euclid):
    pass
