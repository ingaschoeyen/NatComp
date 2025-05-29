import numpy as np
from geometry import *
import math
from enum import Enum
import random


class Strategy(Enum):
    RANDOM = 1 # Vote randomly
    HONEST = 2 # Vote according to personal preferences, polls have no effect
    POPULIST = 3 # Support most popular candidate, personal preferences have no effect
    REALIST = 4 # Support most popular tolerated candidate, support all tolerated if possible
    LOYAL = 5 # Support favourite candidate, support only non-threatening tolerated candidates

class System(Enum):
    FPTP = 1
    INSTANT_RUNOFF = 2
    APPROVAL = 3

class Voter():

    coords : Point
    strat : Strategy
    best_preference : float
    worst_tolerance : float


    def __init__(self, coords : Point, strat : Strategy = Strategy.HONEST):
        self.coords : Point = coords
        self.strat = strat

    def get_tolerance(self, best_distance, worst_distance):
        return (self.best_preference * best_distance + self.worst_tolerance * worst_distance) / 2

    # Tolerated candidates sorted in order of preference
    # TODO optimization: try finding min max first, then filter, and sort last
    def get_tolerated(self, candidates : 'Population', dist_metric = distance_euclid):
        cand_points = [cand.coords for cand in candidates.popul]
        distances = point_distances(self.coords, cand_points, dist_metric)
        sorted_cands = sorted(zip(distances, range(candidates.size())))
        best_dist, best_id = sorted_cands[0]
        worst_dist, worst_id = sorted_cands[-1]
        tolerance = self.get_tolerance(best_dist, worst_dist)
        tolerated = []
        for dist, cand in sorted_cands:
            if dist > tolerance:
                break
            tolerated.append(cand)
        return tolerated

    # Favourite candidate
    def get_favourite(self, candidates : 'Population', dist_metric = distance_euclid):
        cand_points = [cand.coords for cand in candidates.popul]
        return np.argmin(point_distances(self.coords, cand_points, dist_metric))

    def get_votes(self, candidates : 'Population', polls : list[float], system : System, dist_metric = distance_euclid):
        assert candidates.size() == len(polls)
        votes_counts = [0 for _ in range(candidates.size())]

        match system:

            case System.FPTP | System.INSTANT_RUNOFF: # IR is iterated FPTP

                match self.strat:

                    case Strategy.RANDOM:
                        votes_counts[random.randint(0, candidates.size())] += 1

                    case Strategy.HONEST | Strategy.LOYAL:
                        votes_counts[self.get_favourite(candidates, dist_metric)] += 1

                    case Strategy.POPULIST:
                        votes_counts[np.argmax(polls)] += 1

                    case Strategy.REALIST: # Vote for most popular tolerated candidate
                        tolerated = self.get_tolerated(candidates, dist_metric)
                        if len(tolerated) > 0:
                            _, most_pop_tolerated = max(zip([polls[cand] for cand in tolerated], tolerated))
                            votes_counts[most_pop_tolerated] += 1

            case System.APPROVAL:

                match self.strat:

                    case Strategy.RANDOM: # Approve of candidates at random
                        votes_counts = [random.randint(0, 1) for _ in range(candidates.size())]

                    case Strategy.HONEST | Strategy.REALIST: # Approve of tolerated candidates
                        for cand in self.get_tolerated(candidates, dist_metric):
                            votes_counts[cand] += 1

                    case Strategy.POPULIST:
                        votes_counts[np.argmax(polls)] = 1 # Approve only of most popular candidate

                    case Strategy.LOYAL: # Approve of favourite and non-threatening tolerated candidates
                        tolerated = self.get_tolerated(candidates, dist_metric)
                        favourite = tolerated[0] if len(tolerated) > 0 else self.get_favourite(candidates, dist_metric)
                        for cand in tolerated:
                            if polls[cand] < polls[favourite]:
                                votes_counts[cand] += 1
                        votes_counts[favourite] += 1

        return votes_counts

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

    # Get the polls from the population when presented with a list of candidates
    def get_polls(self, candidates : 'Population'):
        pass


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
# Measures the (average) distance between voters and candidates weighted by the results,
# and compares it to average obtained from voting randomly ("worst possible system")
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
