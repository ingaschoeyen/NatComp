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
class Candidate():

    coords : Point

    def __init__(self, coords : Point):
        self.coords : Point = coords

class Voter():

    coords : Point
    strat : Strategy
    best_preference : float
    worst_tolerance : float


    def __init__(self, coords : Point, strat : Strategy, best_preference : float, worst_tolerance : float):
        self.coords = coords
        self.strat = strat
        self.best_preference = best_preference
        self.worst_tolerance = worst_tolerance

    def get_tolerance(self, best_distance, worst_distance):
        return (self.best_preference * best_distance + self.worst_tolerance * worst_distance) / 2

    # Tolerated candidates sorted in order of preference
    # Can be empty
    # TODO optimization: try finding min max first, then filter, and sort last
    def get_tolerated(self, candidates : list[Candidate], dist_metric = distance_euclid):
        cand_points = [cand.coords for cand in candidates]
        distances = point_distances(self.coords, cand_points, dist_metric)
        sorted_cands = sorted(zip(distances, range(len(candidates))))
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
    def get_favourite(self, candidates : list[Candidate], dist_metric = distance_euclid):
        cand_points = [cand.coords for cand in candidates]
        return np.argmin(point_distances(self.coords, cand_points, dist_metric))

    def get_votes(self, candidates : list[Candidate], polls : list[float], system : System, dist_metric = distance_euclid):
        assert len(candidates) == len(polls)
        votes_counts = [0 for _ in range(len(candidates))]

        match system:

            case System.FPTP | System.INSTANT_RUNOFF: # IR is iterated FPTP

                match self.strat:

                    case Strategy.RANDOM:
                        votes_counts[random.randint(0, len(candidates))] += 1

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
                        votes_counts = [random.randint(0, 1) for _ in range(len(candidates))]

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

# TODO get polling results
def get_polls(voters : list[Voter], candidates : list[Candidate], prev_polls : list[float], system : System):
    pass

def trunc_votes(vote_counts : list[int], vote_sum : int, threshold : float):
    return [votes if votes / vote_sum >= threshold else 0 for votes in vote_counts]

def sum_votes(voters : list[Voter], candidates : list[Candidate], polls : list[float],
              system : System, dist_metric = distance_euclid):
    assert len(candidates) > 0
    votes_counts = [0 for _ in range(len(candidates))]

    for voter in voters:
        for i, vote in enumerate(voter.get_votes(candidates, polls, system, dist_metric)):
            votes_counts[i] += vote

    return votes_counts

# First past the post (plurality voting)
# Every voter has only one vote to cast
# Spoiler effect
def fptp(voters : list[Voter], candidates : list[Candidate], polls : list[float], threshold : float = 0.0, dist_metric = distance_euclid):
    votes_counts = sum_votes(voters, candidates, polls, System.FPTP, dist_metric)
    return trunc_votes(votes_counts, len(voters), threshold)

# Instant runoff
# Every voter ranks all candidates in order of preference,
# if the least popular candidate is below threshold
# their voters' votes are transferred to their second preference
# Repeats until everyone with votes is above threshold
# (Iterated FPTP with transferable votes)
# TODO if there are more least favourite parties, eliminate them all
def instant_runoff(voters : list[Voter], candidates : list[Candidate], polls : list[float], threshold : float, dist_metric = distance_euclid):
    final_results = [0 for _ in range(len(candidates))]
    candidates = [Candidate(cand.coords) for cand in candidates]
    polls = polls.copy()
    shifts = [0 for _ in range(len(candidates))]
    results = sum_votes(voters, candidates, polls, System.INSTANT_RUNOFF, dist_metric=dist_metric)
    worst_cand = np.argmin(results)
    while results[worst_cand] / len(voters) < threshold:
        # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
        for i in range(worst_cand, len(candidates) - 1):
            shifts[i] = shifts[i + 1] + 1
        shifts.pop()
        candidates.pop(worst_cand)
        polls.pop(worst_cand)
        results = sum_votes(voters, candidates, polls, System.INSTANT_RUNOFF, dist_metric=dist_metric)
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
def stv(voters : list[Voter], candidates : list[Candidate], threshold : float, dist_metric = distance_euclid):
    pass

# Approval voting
# Every voter can approve of (vote for) any number of candidates
def approval(voters : list[Voter], candidates : list[Candidate], polls : list[float],
             threshold : float, dist_metric = distance_euclid):
    votes_counts = sum_votes(voters, candidates, polls, System.APPROVAL, dist_metric)
    return trunc_votes(votes_counts, len(voters), threshold)

# TODO approval with weighted votes?
# E. g. more votes, less weight each vote has,
# or rank each candidate in percents how much they are approved
# see Borda voting

# TODO approval with a set amount of votes, but able to elect one candidate more than once?
# would be the same as weighted voting with sum of weights equal to 1

def percentage(results : list[int]):
    vote_sum = sum(results)
    return [votes / vote_sum for votes in results]

def total_utility(voters : list[Voter], candidates : list[Candidate], dist_metric = distance_euclid):
    utilities = [0 for _ in range(len(candidates))]
    for i, candidate in enumerate(candidates):
        for voter in voters:
            utilities[i] += dist_metric(candidate.coords, voter.coords)
    return utilities

# Voter satisfaction efficiency - average utility approach
# Measures the (average) distance between voters and candidates weighted by the results,
# and compares it to average obtained from voting randomly ("worst possible system")
# TODO alternatives - measure utility non-linearly, use softmax?
def vse_util(voters : list[Voter], candidates : list[Candidate], results : list[float], dist_metric = distance_euclid):
    assert math.isclose(sum(results), 1.0, rel_tol=1e-4) # <results> must be a distribution on parties

    utilities = total_utility(voters, candidates, dist_metric)
    best = min(utilities)
    current = sum([perc * util for perc, util in zip(results, utilities)])
    random = sum(utilities) / len(utilities)

    assert random >= best # In worst case, we can always vote randomly
    return (random - current) / (random - best) if random - best != 0 else 1 # In case random == best

# TODO Voter satisfaction efficiency - maximise compromise approach
def vse_comp(voters : list[Voter], candidates : list[Candidate], results : list[int], dist_metric = distance_euclid):
    pass
