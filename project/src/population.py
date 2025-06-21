import random
from typing import Any, Optional
import numpy as np
import pandas as pd
from enum import Enum
from geometry import *
from agents import Voter, Candidate, Strategy, Approach, System


class Initialization(Enum):
    UNIFORM = 1
    NORMAL = 2
    # TODO Generate the population in a number of clusters which are similar (close)
    # Simulates how parties (clusters) are composed of similarly thinking, but distinct, candidates (points),
    # or how the voters are divided into similarly thinking groups
    CLUSTER = 3
    # TODO Initialize the population from existing data, e.g. from a file or database
    CUSTOM = 4

default_pop_params = {
    # General parameters
    "campaign_weight": 0.5,  # Weight of the campaign message in the voter's decision
    "poll_weight": 0.3,      # Weight of the polls in the voter's decision
    "social_weight": 0.2,    # Weight of the social influence in the voter's decision
    "dimension": 2,          # Dimension of the space in which voters and candidates are located
    "low": -1,               # Lower bound for the uniform distribution of voter positions
    "high": 1,               # Upper bound for the uniform distribution of voter positions
    "mu": 0,                 # Mean for the normal distribution of voter positions
    "sigma": 1,
    "cand_coord_dist": Initialization.UNIFORM,  # Distribution type for candidate positions: "uniform", "normal", "cluster", or "custom"
    "n_candidates": 10,       # Number of candidates in the election
    "voter_coord_dist": Initialization.UNIFORM, # Distribution type for voter positions: "uniform", "normal", "cluster", or "custom"
    "n_voters": 200,          # Number of voters in the population
    "use_local_neighborhood": False,  # Whether to use local neighborhood for updating voter opinions
    "neighborhood_radius": 0.2,  # Radius for the local neighborhood around
    "per_polls": 0.1,         # Percentage of the subsample size when polling
    # Candidate parameters
    "approach_weight": 0.005,  # Weight of the approach in the candidate's position update
    "cand_approach_dist": {
        Approach.RANDOM : 0.05,
        Approach.HONEST : 0.45,
        Approach.DEFENSIVE : 0.25,
        Approach.OFFENSIVE : 0.25
    },
    # Voter parameters
    "voter_strat_dist": {
        Strategy.RANDOM : 0.05,
        Strategy.HONEST : 0.10,
        Strategy.POPULIST : 0.10,
        Strategy.REALIST : 0.50,
        Strategy.LOYAL : 0.25,
    },
    "best_preference": 1.0,  # Best ideological position for the voter
    "worst_tolerance": 0.8,  # Worst ideological position that the voter tolerates
    "campaign_weight": 0.4,  # Weight of the campaign message in the voter's decision
    "poll_weight": 0.2,  # Weight of the polls in the voter's decision
    "social_weight": 0.6,  # Weight of the social influence in the voter's decision
}

class Population():

    def __init__(self, params: dict[str, Any] = default_pop_params, voters: list[Voter] = None, candidates: list[Candidate] = None):
        self.campaign_weight = params.get("campaign_weight", default_pop_params["campaign_weight"])
        self.poll_weight = params.get("poll_weight", default_pop_params["poll_weight"])
        self.social_weight = params.get("social_weight", default_pop_params["social_weight"])
        self.dimension = params.get("dimension", default_pop_params["dimension"])
        self.low = params.get("low", default_pop_params["low"])
        self.high = params.get("high", default_pop_params["high"])
        self.mu = params.get("mu", default_pop_params["mu"])
        self.sigma = params.get("sigma", default_pop_params["sigma"])
        self.cand_coord_dist = params.get("cand_coord_dist", default_pop_params["cand_coord_dist"])
        self.n_candidates = params.get("n_candidates", default_pop_params["n_candidates"])
        self.cand_approach_dist = params.get("cand_approach_dist", default_pop_params["cand_approach_dist"])
        self.voter_coord_dist = params.get("voter_coord_dist", default_pop_params["voter_coord_dist"])
        self.n_voters = params.get("n_voters", default_pop_params["n_voters"])
        self.voter_strat_dist = params.get("voter_strat_dist", default_pop_params["voter_strat_dist"])
        self.use_local_neighborhood = params.get("use_local_neighborhood", default_pop_params["use_local_neighborhood"])
        self.neighborhood_radius = params.get("neighborhood_radius", default_pop_params["neighborhood_radius"])
        self.per_polls = params.get("per_polls", default_pop_params["per_polls"])

        self.candidates = candidates if candidates else self.init_candidates(params=params)
        self.voters = voters if voters else self.init_voters(params=params)
        self.elected_candidates = [i for i in range(len(self.candidates))]

    def get_strategies(self):
        voter_strategies = [voter.strat.value for voter in self.voters]
        cand_approaches = [cand.approach.value for cand in self.candidates]
        return voter_strategies, cand_approaches

    def init_candidates(self, params: dict = None):
        approaches = random.choices(list(Approach), weights=self.cand_approach_dist.values(), k=self.n_candidates)
        match self.cand_coord_dist:
            case Initialization.UNIFORM:
                return [Candidate([float(np.random.uniform(self.low, self.high)) for _ in range(self.dimension)], i, approach=approaches[i], params=params) for i in range(self.n_candidates)]
            case Initialization.NORMAL:
                return [Candidate([float(np.random.normal(self.mu, self.sigma)) for _ in range(self.dimension)], i, approach=approaches[i], params=params) for i in range(self.n_candidates)]
            case Initialization.CLUSTER:
                pass # TODO Implement cluster distribution for candidates
            case Initialization.CUSTOM:
                pass # TODO Implement custom distribution for candidates

    def init_voters(self, params: dict = None):
        strategies = random.choices(list(Strategy), weights=self.voter_strat_dist.values(), k=self.n_voters)
        match self.cand_coord_dist:
            case Initialization.UNIFORM:
                return [Voter(coords=[np.random.uniform(self.low, self.high, self.dimension)], strat=strategies[i], params=params, id = i) for i in range(self.n_voters)]
            case Initialization.NORMAL:
                return [Voter(coords=[np.random.normal(self.mu, self.sigma) for _ in range(self.dimension)], strat=strategies[i], params=params, id = i) for i in range(self.n_voters)]
            case Initialization.CLUSTER:
                pass # TODO Implement cluster distribution for candidates
            case Initialization.CUSTOM:
                pass # TODO Implement custom distribution for candidates

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
            "candidate_id": [cand.id for cand in self.candidates],
            "candidate_coords": [cand.coords for cand in self.candidates],
            "avg_voter_position": [cand.avg_voter_position for cand in self.candidates]
            })

    def take_poll(self, system: System, last_poll: Optional[list[float]] = None):
        """
        Returns a list of percentages of votes sampled from a subset of the population, where each percentage corresponds to a candidate.
        """
        # sample voters for polls
        subsample_size = int(len(self.voters) * self.per_polls)
        sampled_voters = np.random.choice(self.voters, subsample_size, replace=False)
        # Count votes for each candidate
        vote_counts = [0 for _ in range(len(self.candidates))]
        avg_voter_position = [(0, 0) for _ in range(len(self.candidates))]  # Initialize average voter positions for candidates
        for voter in sampled_voters:

            votes = voter.get_votes(self.candidates, system, last_poll)

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

    def local_neighborhood(self, voter: Voter, system: System, polls: list[float] = None, dist_metric = distance_euclid):
        """
        Returns a list of percentages of votes from the local neighborhood of the voter,
        where each percentage corresponds to a candidate.
        The neighborhood is defined as all voters within a given radius from the voter.
        """
        neighborhood_votes = [0 for _ in range(len(self.candidates))]
        for other_voter in self.voters:
            if distance_euclid(voter.coords, other_voter.coords) <= self.neighborhood_radius:
                top_candidate_index = np.argmin(other_voter.get_votes(candidates=self.candidates, system=system, polls=polls, dist_metric=dist_metric))
                neighborhood_votes[top_candidate_index] += 1
        total_votes = sum(neighborhood_votes)
        return [votes / total_votes if total_votes > 0 else 0 for votes in neighborhood_votes]

    def update_voters(self, system: System, polls=None, distance_metric=distance_euclid):
        """
        Updates the voters' voting preferences based on the current candidates and polls.
        If polls are provided, they are used to adjust the voters' preferences.
        """
        for voter in self.voters:
            loc_neigh = None if not self.use_local_neighborhood else self.local_neighborhood(voter, system, polls, distance_metric)
            voter.update_votes(self.candidates, system=system, dist_metric=distance_metric, polls=polls,
                local_neighborhood=loc_neigh,
                campaigns=[cand.coords for cand in self.candidates])

    # Candidate position update based on the average position of the voters (theirs or oppositions)
    def campaign_voters(self, avg_voter_position: list[Point] = None, polls: list[float] = None):
        """
        Updates the candidates' positions based on the voters' preferences and campaigns.
        This can include adjusting their positions to better align with the average position of voters who voted for them.
        """
        for candidate in self.candidates:
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
                    return

    # Candidate position update based on the position of other candidates
    def campaign_candidates(self, results: list[float] = None):
        """
        Simulates campaigning by candidates, which can include adjusting their positions based on the average voter position.
        This can be implemented as a separate method or integrated into the update_candidates method.
        """
        if results is None:
            return

        for candidate in self.candidates:
            match candidate.approach:
                case Approach.RANDOM:
                    # Randomly adjust candidate position within a small range
                    candidate.coords[0] += np.random.uniform(-0.1, 0.1)
                    candidate.coords[1] += np.random.uniform(-0.1, 0.1)
                case Approach.DEFENSIVE:
                    candidate.coords = candidate.campaign_coords
                case Approach.OFFENSIVE:
                    target_location = self.candidates[np.argmax(results)].coords if results is not None else candidate.coords
                    candidate.update_position(target_location)
                case Approach.HONEST:
                    return # Honest candidates do not change their position
