import numpy as np
from geometry import *
from agents import Voter, Candidate, System


def trunc_votes(vote_counts : list[int], vote_sum : int, threshold : float):
    return [votes if votes / vote_sum >= threshold else 0 for votes in vote_counts]

def sum_votes(voters : list[Voter], candidates : list[Candidate], polls : list[float],
              system : System, dist_metric = distance_euclid):
    assert len(candidates) > 0
    votes_counts = [0 for _ in range(len(candidates))]

    for voter in voters:
        for i, vote in enumerate(voter.get_votes(candidates=candidates, polls=polls, system=system, dist_metric=dist_metric)):
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

def percentage(votes_counts : list[int]):
    vote_sum = sum(votes_counts)
    return [votes / vote_sum for votes in votes_counts] if vote_sum != 0 else [0 for _ in votes_counts]

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
    assert np.isclose(sum(results), 1), f'vse_util error, sum of results is {sum(results)}, results are {results}' # <results> must be a distribution on parties

    utilities = total_utility(voters, candidates, dist_metric)
    best = min(utilities)
    current = sum([perc * util for perc, util in zip(results, utilities)])
    random = sum(utilities) / len(utilities)

    assert random >= best, f'vse_util error, worst case, best = {best}' # In worst case, we can always vote randomly
    return (random - current) / (random - best) if random - best != 0 else 1 # In case random == best

# TODO Voter satisfaction efficiency - maximise compromise approach
def vse_comp(voters : list[Voter], candidates : list[Candidate], results : list[float], dist_metric = distance_euclid):
    utilities = total_utility(voters, candidates, dist_metric)
    current = [perc * util for perc, util in zip(results, utilities)]

    mean_val = np.mean(current)
    std_dev = np.std(current)

    if np.isclose(std_dev, 0):
        return 1.0  # Perfect uniformity

    if np.isclose(mean_val, 0):
        return 0.0  # Avoid division by zero; implies minimal utility overall

    # Uniformity = 1 - Coefficient of Variation
    score = 1 - (std_dev / mean_val)
    return max(0.0, min(1.0, score))

def vse_vdist_comp(voters : list[Voter], candidates : list[Candidate], results : list[float], dist_metric = distance_euclid):
    assert np.isclose(sum(results), 1), f'vse_vdist_comp error, sum of results is {sum(results)}, results are {results}' # <results> must be a distribution on parties

    weighted_sums = []
    for voter in voters:
        dists = [dist_metric(voter.coords, cand.coords) for cand in candidates]
        weighted_sum = sum(perc * d for perc, d in zip(results, dists))
        weighted_sums.append(weighted_sum)

    mean_val = np.mean(weighted_sums)
    std_dev = np.std(weighted_sums)

    if np.isclose(std_dev, 0):
        return 1.0
    if np.isclose(mean_val, 0):
        return 0.0

    uniformity_score = 1 - (std_dev / mean_val)
    return max(0.0, min(1.0, uniformity_score))
