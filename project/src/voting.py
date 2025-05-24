import numpy as np
from geometry import *
import math

# TODO Voter might be more complex, i. e. in their strategy of how honestly they vote
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
    def init_custom(self):
        pass

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


def trunc_votes(vote_counts : list[int], vote_sum : int, threshold : float):
    return [votes if votes / vote_sum >= threshold else 0 for votes in vote_counts]

# First past the post (Instant runoff/plurality)
# Every voter has one vote to cast
# Spoiler effect
def fptp(voters : Population, candidates : Population, threshold : float = 0.0, dist_metric = distance_euclid):
    assert candidates.size() > 0

    vote_counts = [0 for _ in range(candidates.size())]
    for favourite in closest_points(voters.popul, candidates.popul, dist_metric):
        vote_counts[favourite] += 1

    return trunc_votes(vote_counts, voters.size(), threshold) if threshold > 0 else vote_counts

# Approval voting - relative to best and worst candidate
# Every voter can approve of (vote for) any number of candidates
# Approval range of a voter is weighted average of distance to best and worst candidate
def approval_rel(voters : Population, candidates : Population, best_preference : float, worst_tolerance : float, dist_metric = distance_euclid):
    votes_counts= [0 for _ in range(candidates.size())]
    for voter in voters.popul:
        candidate_ranks = point_distances(voter, candidates.popul, dist_metric)
        best_cand_dist, worst_cand_dist = min(candidate_ranks), max(candidate_ranks)
        weighted_avg = (best_cand_dist * best_preference + worst_cand_dist * worst_tolerance) / 2
        for i, cand_rank in enumerate(candidate_ranks):
            if cand_rank <= weighted_avg:
                votes_counts[i] += 1

    return votes_counts

# TODO approval with weighted votes?
# E. g. more votes, less weight each vote has,
# or rank each candidate in percents how much they are approved
# see Borda voting

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
    final_results = [0 for _ in range(candidates.size())]
    candidates = candidates.copy()
    shifts = [0 for _ in range(candidates.size())]
    results = fptp(voters, candidates, dist_metric=dist_metric)
    worst_cand = np.argmin(results)
    while results[worst_cand] / voters.size() < threshold:
        # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
        for i in range(worst_cand, candidates.size() - 1):
            shifts[i] = shifts[i + 1] + 1
        shifts.pop()
        candidates.pop(worst_cand)
        results = fptp(voters, candidates, dist_metric=dist_metric)
        worst_cand = np.argmin(results)

    # Map votes of non-eliminated candidates back to original indices
    for i, res in enumerate(results):
        final_results[i + shifts[i]] = res

    return final_results


# TODO (*Complete*) single transferable vote ranked choice voting
# Every voter ranks *all* candidates in order of preference
# If a preferred candidate is not selected, the vote is transfered to a lower ranked candidate
# Requires a threshold for selecting a candidate (percentage of all votes required)
# Implemented as used in Malta parliamentary elections, but using a set threshold (instead of Droop quota)
# TODO can also use the Droop quota as threshold, requires number of mandates to distribute
# TODO incomplete stv - rank only a subset of candidates, lowers voting power of voters, requires threshold as in approval
# TODO PROBLEM - what is the percentage result of the candidate? The amount of the total votes (above threshold)?
# If so, need to keep in check how many votes were transferred
def stv(voters : Population, candidates : Population, threshold : float, dist_metric = distance_euclid):
    pass

def percentage(results : list[int]):
    vote_sum = sum(results)
    return [votes / vote_sum for votes in results]

def total_utility(voters : Population, candidates : Population, dist_metric = distance_euclid):
    utilities = [0 for _ in range(candidates.size())]
    for i, candidate in enumerate(candidates.popul):
        for voter in voters.popul:
            utilities[i] += dist_metric(candidate, voter)
    return utilities

# Voter satisfaction efficiency - average utility approach
# Measures the (average) weighted distance between voters and candidates
# TODO alternatives - measure utility non-linearly, use softmax?
def vse_util(voters : Population, candidates : Population, results : list[float], dist_metric = distance_euclid):
    assert math.isclose(sum(results), 1.0, rel_tol=1e-4) # <results> must be a distribution on parties

    utilities = total_utility(voters, candidates, dist_metric)
    best = min(utilities)
    current = sum([perc * util for perc, util in zip(results, utilities)])
    random = sum(utilities) / len(utilities)

    assert random >= best # In worst case, we can always vote randomly
    return (random - current) / (random - best) if random - best != 0 else 1 # In case random == best

# TODO Voter satisfaction efficiency - maximise compromise approach
def vse_comp(voters : Population, candidates : Population, results : list[int], dist_metric = distance_euclid):
    pass
