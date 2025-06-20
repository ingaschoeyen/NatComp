from population import Population
from geometry import *
import numpy as np
from enum import Enum
from voter import Voter, Candidate, System
from plotting import plot_closest, plot_approved, plot_bar, plot_pie



example_election_params = {
    "election_type": System.FPTP,  # Type of election: "fptp", "approval_rel", "instant_runoff", "stv"
    "threshold": 0.1,         # Threshold for the minimum percentage of votes required for a candidate to be considered
    "dist_metric": "euclid"   # Distance metric to use for calculating distances between voters and candidates
}



class Election():

    def __init__(self, params: dict = example_election_params, system: System = System.FPTP):
        self.params = params
        self.system = system


    def trunc_votes(self, vote_counts : list[int], vote_sum : int, threshold : float):
        return [votes if votes / vote_sum >= threshold else 0 for votes in vote_counts]

    def sum_votes(self, mytypavoters: list[Voter], candidates: list[Candidate], polls : list[float],
                system : System, dist_metric = distance_euclid):
        assert len(candidates) > 0
        votes_counts = [0 for _ in range(len(candidates))]

        for voter in mytypavoters:
            for i, vote in enumerate(voter.get_votes(candidates, system, polls, dist_metric)):
                votes_counts[i] += vote

        return votes_counts

    # First past the post (plurality voting)
    # Every voter has only one vote to cast
    # Spoiler effect
    def fptp(self, voters : list[Voter], candidates : list[Candidate], polls : list[float], threshold : float = 0.0, dist_metric = distance_euclid):
        votes_counts = self.sum_votes(voters, candidates, polls, System.FPTP, dist_metric)
        return self.trunc_votes(votes_counts, len(voters), threshold)

    # Instant runoff
    # Every voter ranks all candidates in order of preference,
    # if the least popular candidate is below threshold
    # their voters' votes are transferred to their second preference
    # Repeats until everyone with votes is above threshold
    # (Iterated FPTP with transferable votes)
    # TODO if there are more least favourite parties, eliminate them all
    def instant_runoff(self, voters : list[Voter], candidates : list[Candidate], polls : list[float], threshold : float, dist_metric = distance_euclid):
        final_results = [0 for _ in range(len(candidates))]
        candidates = [Candidate(cand.coords) for cand in candidates]
        polls = polls.copy()
        shifts = [0 for _ in range(len(candidates))]
        results = self.sum_votes(voters, candidates, polls, System.INSTANT_RUNOFF, dist_metric=dist_metric)
        worst_cand = np.argmin(results)
        while results[worst_cand] / len(voters) < threshold:
            # Move candidates with higher id than worst_cand to the left by 1, and add 1 to their shift
            for i in range(worst_cand, len(candidates) - 1):
                shifts[i] = shifts[i + 1] + 1
            shifts.pop()
            candidates.pop(worst_cand)
            polls.pop(worst_cand)
            results = self.sum_votes(voters, candidates, polls, System.INSTANT_RUNOFF, dist_metric=dist_metric)
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
    def approval(self, voters : list[Voter], candidates : list[Candidate], polls : list[float],
                threshold : float, dist_metric = distance_euclid):
        votes_counts = self.sum_votes(voters, candidates, polls, System.APPROVAL, dist_metric)
        return self.trunc_votes(votes_counts, len(voters), threshold)

    # TODO approval with weighted votes?
    # E. g. more votes, less weight each vote has,
    # or rank each candidate in percents how much they are approved
    # see Borda voting

    # TODO approval with a set amount of votes, but able to elect one candidate more than once?
    # would be the same as weighted voting with sum of weights equal to 1

    def percentage(self, votes_counts : list[int]):
        vote_sum = sum(votes_counts)
        return [votes / vote_sum for votes in votes_counts] if vote_sum != 0 else [0 for _ in votes_counts]

    def total_utility(self, voters : list[Voter], candidates : list[Candidate], dist_metric = distance_euclid):
        utilities = [0 for _ in range(len(candidates))]
        for i, candidate in enumerate(candidates):
            for voter in voters:
                utilities[i] += dist_metric(candidate.coords, voter.coords)
        return utilities

    # Voter satisfaction efficiency - average utility approach
    # Measures the (average) distance between voters and candidates weighted by the results,
    # and compares it to average obtained from voting randomly ("worst possible system")
    # TODO alternatives - measure utility non-linearly, use softmax?
    def vse_util(self, voters : list[Voter], candidates : list[Candidate], results : list[float], dist_metric = distance_euclid):
        assert np.isclose(sum(results), 1) # <results> must be a distribution on parties

        utilities = self.total_utility(voters, candidates, dist_metric)
        best = min(utilities)
        current = sum([perc * util for perc, util in zip(results, utilities)])
        random = sum(utilities) / len(utilities)

        assert random >= best # In worst case, we can always vote randomly
        return (random - current) / (random - best) if random - best != 0 else 1 # In case random == best

    # TODO Voter satisfaction efficiency - maximise compromise approach
    def vse_comp(self, voters : list[Voter], candidates : list[Candidate], results : list[float], dist_metric = distance_euclid):
        utilities = self.total_utility(voters, candidates, dist_metric)
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

    def vse_vdist_comp(self, voters : list[Voter], candidates : list[Candidate], results : list[float], dist_metric = distance_euclid):
        assert np.isclose(sum(results), 1) # <results> must be a distribution on parties

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

    def do_an_election(self, mycoolvoters, candidates, polls: list[float] = None, dist_metric = distance_euclid):
        votes_counts = self.sum_votes(mytypavoters=mycoolvoters, candidates=candidates, polls=polls, system=self.system, dist_metric=dist_metric)
        results = self.percentage(votes_counts)
        vse_util = self.vse_util(mycoolvoters, candidates, results, dist_metric)
        vse_comp = self.vse_comp(mycoolvoters, candidates, results, dist_metric)
        vse_vdist_comp = self.vse_vdist_comp(mycoolvoters, candidates, results, dist_metric)
        norm_entropy = compute_norm_entropy(results)
        return votes_counts, results, vse_util, vse_comp, vse_vdist_comp, norm_entropy

    def plot_an_election(self, voters: list[Voter], candidates: list[Candidate],
                         votes_counts: list[int], results: list[float], output_path: str = None, dist_metric = distance_euclid):
        if output_path is None:
            output_path = f"./election_{self.system.name.lower()}.png"
        plot_closest(voters, candidates, output_path=output_path.replace(".png", "_closest.png"))
        plot_bar(votes_counts, output_path=output_path.replace(".png", "_bar.png"))
        plot_pie(votes_counts, output_path=output_path.replace(".png", "_pie.png"))
        plot_approved(voters, candidates, output_path=output_path.replace(".png", "_approved.png"))
        return output_path

