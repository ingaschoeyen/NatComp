from typing import Optional
import numpy as np
from geometry import *
import math
from voter import Voter, Candidate, Strategy, Approach, System
import pandas as pd


example_population_params = {
    "campaign_weight": 0,  # Weight of the campaign message in the voter's decision
    "poll_weight": 0.05,      # Weight of the polls in the voter's decision
    "social_weight": 0.1,    # Weight of the social influence in the voter's decision
    "threshold": 0.05,        # Threshold for the minimum percentage of votes required for a candidate to be considered
    "dimension": 2,          # Dimension of the space in which voters and candidates are located
    "low": -1,               # Lower bound for the uniform distribution of voter positions
    "high": 1,               # Upper bound for the uniform distribution of voter positions
    "mu": 0,                 # Mean for the normal distribution of voter positions
    "cand_dist": "uniform",  # Distribution type for candidate positions: "uniform", "normal", "cluster", or "custom"
    "n_candidates": 10,       # Number of candidates in the election
    "voter_dist": "uniform", # Distribution type for voter positions: "uniform", "normal", "cluster", or "custom"
    "n_voters": 200,          # Number of voters in the population
    "local_neighborhood": True,  # Whether to use local neighborhood for updating voter opinions
    "neighborhood_radius": 0.2,  # Radius for the local neighborhood around
    "per_polls": 0.1         # Percentage of the subsample size when polling
}


class Population():

    def __init__(self, params: dict = None, voters: list[Voter] = None, candidates: list[Candidate] = None):
        self.params = params if params is not None else example_population_params
        self.cands = candidates
        self.init_canidates(params)
        self.voters = voters
        self.init_voters(params)
        self.elected_candidates = [i for i in range(len(self.cands))]


    def get_strategies(self):
        voter_strategies = [voter.strat.value for voter in self.voters]
        cand_approaches = [cand.approach.value for cand in self.cands]
        return voter_strategies, cand_approaches

    def init_canidates(self, params: dict = None):
        if params is None:
            params = example_population_params

        if self.cands is not None:
            pass
        else:
            n_candidates = params.get("n_candidates", 3)
            dimension = params.get("dimension", 2)
            low = params.get("low", -1)
            high = params.get("high", 1)
            if params.get("cand_dist", "uniform") == "normal":
                mu = params.get("mu", 0)
                sigma = params.get("sigma", 1)
                self.cands = [Candidate([float(np.random.normal(mu, sigma)) for _ in range(dimension)], i, approach=np.random.choice(list(Approach))) for i in range(n_candidates)]
            elif params.get("cand_dist", "uniform") == "cluster":
                self.cands = []
                # TODO Implement cluster distribution for candidates
            elif params.get("cand_dist", "uniform") == "custom":
                self.cands = []
                # TODO Implement custom distribution for candidates
            else:  # Default to uniform distribution
                self.cands = [Candidate([float(np.random.uniform(low, high)) for _ in range(dimension)], i, approach=np.random.choice(list(Approach))) for i in range(n_candidates)]

    def init_voters(self, params: dict = None):
        if params is None:
            params = example_population_params
        if self.voters is not None:
            pass
        else:
            n_voters = params.get("n_voters", 100)
            dimension = params.get("dimension", 2)
            low = params.get("low", -1)
            high = params.get("high", 1)

            if params.get("voter_dist", "uniform") == "normal":
                mu = params.get("mu", 0)
                sigma = params.get("sigma", 1)
                self.voters = [Voter(coords=[np.random.normal(mu, sigma) for _ in range(dimension)], strat=np.random.choice(list(Strategy)), parameters=params, id = i) for i in range(n_voters)]
            elif params.get("voter_dist", "uniform") == "cluster":
                self.voters = []
                # TODO Implement cluster distribution for voters
            elif params.get("voter_dist", "uniform") == "custom":
                self.voters = []
                # TODO Implement custom distribution for voters
            else:
                # Default to uniform distribution
                self.voters = [Voter(coords=[np.random.uniform(low, high, dimension)], strat=np.random.choice(list(Strategy)), parameters=params, id = i) for i in range(n_voters)]

    def init_from_data(self, voters: list[Voter], candidates: list[Candidate]):

        pass  # TODO Initialize the population from existing data, e.g. from a file or database

    def get_voters(self):
        return [voter for voter in self.voters]

    def get_population(self):
        """
        Returns the position of voters and candidates in pandas Dataframe.
        """
        return pd.DataFrame({
            "voter_id": [voter.id for voter in self.voters],
            "voter_coords": [voter.coords for voter in self.voters],
            "vote": [np.argmin(voter.votes) for voter in self.voters],
            "candidate_id": [cand.id for cand in self.cands],
            "candidate_coords": [cand.coords for cand in self.cands],
            "avg_voter_position": [cand.avg_voter_position for cand in self.cands]
            })

    def take_poll(self, system: System, last_poll: Optional[list[float]] = None, candidates: list[Candidate] = None):
        """
        Returns a list of percentages of votes sampled from a subset of the population, where each percentage corresponds to a candidate.
        """

        if candidates is None:
            try:
                candidates = self.cands
            except AttributeError:
                raise ValueError("No candidates provided and no candidates initialized in the population.")

        per_polls = self.params.get("per_polls", 0.1)
        subsample_size = int(len(self.voters) * per_polls)

        # sample voters for polls
        sampled_voters = np.random.choice(self.voters, subsample_size, replace=False)
        # Count votes for each candidate
        vote_counts = [0 for _ in range(len(self.cands))]
        avg_voter_position = [(0, 0) for _ in range(len(self.cands))]  # Initialize average voter positions for candidates
        for voter in sampled_voters:

            # Find the closest candidate to the voter
            # top_candidate_index = voter.get_voting_preferences()
            # Increment the vote count for the top candidate
            # vote_counts[top_candidate_index] += 1

            votes = voter.get_votes(candidates, system, last_poll)

            for cand, cand_votes in enumerate(votes):
                vote_counts[cand] += votes[cand]

                if cand_votes > 0:
                    avg_voter_position[cand] = (
                        avg_voter_position[cand][0] + voter.coords[0][0],
                        avg_voter_position[cand][1] + voter.coords[0][1]
                    )

        # Normalize vote counts to percentages
        distributed_votes = sum(vote_counts)
        polls = [votes / distributed_votes for votes in vote_counts]
        # Calculate average voter position for each candidate
        # TODO some voting systems may allow more votes for one candidate from one voter,
        # so this would not be the average position
        avg_voter_position = [
            (avg[0] / vote_counts[i] if vote_counts[i] > 0 else 0,
             avg[1] / vote_counts[i] if vote_counts[i] > 0 else 0)
            for i, avg in enumerate(avg_voter_position)
        ]
        return polls, avg_voter_position

    def local_neighborhood(self, voter: Voter, radius: float = 0.1):
        """
        Returns a list of percentages of votes from the local neighborhood of the voter,
        where each percentage corresponds to a candidate.
        The neighborhood is defined as all voters within a given radius from the voter.
        """
        neighborhood_votes = [0 for _ in range(len(self.cands))]
        for other_voter in self.voters:
            if distance_euclid(voter.coords, other_voter.coords) <= radius:
                top_candidate_index = np.argmin(other_voter.votes)
                neighborhood_votes[top_candidate_index] += 1
        total_votes = sum(neighborhood_votes)
        return [votes / total_votes if total_votes > 0 else 0 for votes in neighborhood_votes]

    def update_voter_opinions(self, system: System, polls=None, candidates: list[Candidate] = None,  distance_euclid=distance_euclid):
        """
        Updates the voters' voting preferences based on the current candidates and polls.
        If polls are provided, they are used to adjust the voters' preferences.
        """

        if candidates is None:
            try:
                candidates = self.cands
            except AttributeError:
                raise ValueError("No candidates provided and no candidates initialized in the population.")


        for voter in self.voters:
            if self.params.get("local_neighborhood", False):
                local_neighborhood = None
            else:
                local_neighborhood = self.local_neighborhood(voter, radius=self.params.get("neighborhood_radius", 0.1))
            voter.update_voting_preferences(candidates,
                                          system=system,
                                          dist_metric=distance_euclid,
                                          polls=polls,
                                          local_neighborhood=local_neighborhood,
                                          campaigns=[cand.coords for cand in self.cands])

    # TODO this is the same as update_voter_opinions?
    def update_voters(self, system: System):
        gov_candidates = [self.cands[i] for i in self.elected_candidates]
        for voter in self.voters:
            voter.update_voting_preferences(gov_candidates,
                                            system=system,
                                          dist_metric=distance_euclid,
                                          polls=None,
                                          local_neighborhood=None,
                                          campaigns=[cand.coords for cand in gov_candidates])

    # TODO (*Complete*) Update the candidates based on voters' preferences and campaigns
    def campaign(self, candidates: list[Candidate] = None, avg_voter_position=None, polls=None):
        """
        Updates the candidates' positions based on the voters' preferences and campaigns.
        This can include adjusting their positions to better align with the average position of voters who voted for them.
        """
        if candidates is None:
            try:
                candidates = self.cands
            except AttributeError:
                raise ValueError("No candidates provided and no candidates initialized in the population.")
        if avg_voter_position is None:
                raise ValueError("Average voter position must be provided to update candidates.")
        for candidate in candidates:
            match candidate.approach:
                case Approach.RANDOM:
                    # Randomly adjust candidate position within a small range
                    candidate.coords[0] += np.random.uniform(-0.1, 0.1)
                    candidate.coords[1] += np.random.uniform(-0.1, 0.1)
                case Approach.DEFENSIVE:
                    candidate.avg_voter_position = avg_voter_position[candidate.id] if avg_voter_position is not None else candidate.coords
                    candidate.make_campaign()
                case Approach.OFFENSIVE:
                    candidate.avg_voter_position = avg_voter_position[np.argmax(polls)] if avg_voter_position is not None else candidate.coords
                    candidate.make_campaign()
                case Approach.HONEST:
                    pass

    def update_candidates(self, results: list[float] = None):
        """
        Simulates campaigning by candidates, which can include adjusting their positions based on the average voter position.
        This can be implemented as a separate method or integrated into the update_candidates method.
        """

        if results is None:
            pass
        else:
            self.elected_candidates = [candidate.id for candidate in self.cands if results[candidate.id]>= self.params.get('threshold_gov', 0.05)]
            for candidate in self.cands:
                # check if candidate got enough votes to be considered this round
                match candidate.approach:
                    case Approach.RANDOM:
                        # Randomly adjust candidate position within a small range
                        candidate.coords[0] += np.random.uniform(-0.1, 0.1)
                        candidate.coords[1] += np.random.uniform(-0.1, 0.1)
                    case Approach.DEFENSIVE:
                        candidate.coords = candidate.campaign_coords
                    case Approach.OFFENSIVE:
                        target_location = self.cands[np.argmax(results)].coords if results is not None else candidate.coords
                        candidate.update_position(target_location)
                    case Approach.HONEST:
                        # Honest candidates do not change their position
                        pass
