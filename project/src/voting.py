import numpy as np
import scipy
from geometry import *

# TODO Voter ight be more complex, i. e. in their strategy of how honestly they vote
Voter = Point

class Population():

    popul : list[Voter] # Population

    def __init__(self):
        self.popul : list[Voter] = []

    # Uniform distribution
    def init_uniform(self, n: int, dimension: int = 2, low: int = -1, high: int = 1):
        self.popul = [[np.random.uniform(low, high) for _ in range(dimension)] for _ in range(n)]

    # Normal (Gaussian) distribution
    def init_normal(self, n: int, dimension: int = 2, mu: float = 0, sigma: float = 1):
        self.popul = [[np.random.normal(mu, sigma) for _ in range(dimension)] for _ in range(n)]

    # TODO Cluster distribution
    # Generate the population in a number of clusters which are similar (close)
    # Simulates how parties (clusters) are composed of similarly thinking, but distinct, candidates (points),
    # or how the voters are divided into similarly thinking groups
    def init_cluster(self, n: int, dimension: int = 2):
        pass

    # TODO Custom initial setups based on available data

    # TODO Update the population based on polls and/or previous results
    def update(self, polls):
        pass

    def pop(self, index = -1):
        return self.popul.pop(index)

    def copy(self):
        res_copy = Population()
        res_copy.popul = self.popul.copy()
        return res_copy

    def size(self):
        return len(self.popul)


# First past the post (Instant runoff/plurality)
# Every voter has one vote to cast
# Spoiler effect
def fptp(voters : Population, candidates : Population, dist_metric = distance_euclid):
    assert candidates.size() > 0

    vote_count = [0 for _ in range(candidates.size())]
    for favourite in closest_points(voters.popul, candidates.popul, dist_metric):
        vote_count[favourite] += 1

    return vote_count

# Approval voting - relative to best and worst candidate
# Every voter can approve of (vote for) any number of candidates
# If candidates rank is at most <threshold> % of distance between the rank of best and worst candidate, they are approved
# (Always approves at least the best candidate)
def approval_rel(voters : Population, candidates : Population, threshold : float, dist_metric = distance_euclid):
    vote_count = [0 for _ in range(candidates.size())]
    for voter in voters.popul:
        candidate_ranks = point_distances(voter, candidates, dist_metric)
        best_cand_dist, worst_cand_dist = min(candidate_ranks), max(candidate_ranks)
        best_worst_dist = worst_cand_dist - best_cand_dist
        for i, cand_rank in enumerate(candidate_ranks):
            if (cand_rank - best_cand_dist) / best_worst_dist <= threshold:
                vote_count[i] += 1

# Approval voting - relative only to worst candidate (absolute merit)
# Every voter can approve of (vote for) any number of candidates
# If candidate is at most <threshold> % of distance to worst candidate close to the voter, they are approved
# (Might not approve anyone)
def approval_abs(voters : Population, candidates : Population, threshold : float, dist_metric = distance_euclid):
    vote_count = [0 for _ in range(candidates.size)]
    for voter in voters.popul:
        candidate_ranks = point_distances(voter, candidates, dist_metric)
        worst_cand_dist = max(candidate_ranks)
        for i, cand_rank in enumerate(candidate_ranks):
            if (cand_rank / worst_cand_dist) <= threshold:
                vote_count[i] += 1

# TODO approval with weighted votes?
# E. g. more votes, less weight each vote has,
# or rank each candidate in percents how much they are approved

# TODO approval with a set amount of votes, but able to elect one candidate more than once?
# would be the same as weighted voting with sum of weights equal to 1

# Instant runoff
# Every voter ranks all candidates in order of preference,
# if the least popular candidate is below threshold
# (percentage of their votes is lower than <threshold> % of total),
# their voters' votes are transferred to the second preference
# Repeats until everyone with votes is above threshold
# (Implemented as iterated fptp with elimination of weakest)
# TODO might be a way to optimize this
# TODO if there are more least favourite parties, eliminate them all
def instant_runoff(voters : Population, candidates : Population, threshold : float, dist_metric = distance_euclid):
    candidates = candidates.copy()
    shifts = [0 for _ in range(candidates.size())]
    results = fptp(voters, candidates, dist_metric)
    worst_cand = np.argmin(results)
    while results[worst_cand] / voters.size() <= threshold:
        # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
        for i in range(worst_cand, candidates.size() - 1):
            shifts[i] = shifts[i + 1] + 1
        shifts.pop()
        candidates.pop(worst_cand)
        results = fptp(voters, candidates, dist_metric)
        worst_cand = np.argmin(results)

    # Map votes of non-eliminated candidates back to original indices
    final_results = [0 for _ in range(candidates.size())]
    for i, res in results:
        final_results[i + shifts[i]] = res

    return final_results


# TODO (*Complete*) single transferable vote ranked choice voting
# Every voter ranks *all* candidates in order of preference
# If a preferred candidate is not selected, the vote is transfered to a lower ranked candidate
# Requires a threshold for selecting a candidate (percentage of all votes required)
# Implemented as used in Malta parliamentary elections, but using a set threshold (instead of Droop quota)
# TODO can also use the Droop quota as threshold, requires number of mandates to distribute
# TODO incomplete stv - rank only a subset of candidates, lowers voting power of voters, requires threshold as in approval
# TODO ISSUE - what is the percentage result of the candidate? The amount of the total votes (above threshold)?
# If so, need to keep in check how many votes were transferred
def stv(voters : Population, candidates : Population, threshold : float, dist_metric = distance_euclid):
    pass

# Softmax to create percentages from number of received votes
def percentage_distribution(results : list[int]):
    return scipy.softmax(results)

# TODO Voter satisfaction efficiency
def vse(voters : Population, candidates : Population, results : list[int], dist_metric = distance_euclid):
    pass
