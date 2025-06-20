from typing import Optional
from geometry import *
import numpy as np
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

class Approach(Enum):
    RANDOM = 1
    DEFENSIVE = 2
    OFFENSIVE = 3
    HONEST = 4

example_voter_params = {
    "n_candidates": 10,  # Number of candidates in the election
    "best_preference": 0.5,  # Best ideological position for the voter
    "worst_tolerance": 0.1,  # Worst ideological position that the voter tolerates
    "campaign_weight": 0.4,  # Weight of the campaign message in the voter's decision
    "poll_weight": 0.2,  # Weight of the polls in the voter's decision
    "social_weight": 0.6,  # Weight of the social influence in the voter's decision
}

example_candidate_params = {
    "approach_weight": 0.005,  # Weight of the approach in the candidate's position update
}


class Candidate():

    coords : Point
    id: int  # Unique identifier for the candidate
    votes: int  # Number of votes received by this candidate
    vote_history: list[int]  # History of votes received by this candidate

    def __init__(self, coords : Point, id : int= 0, approach: Approach = Approach.RANDOM, params: dict = None):
        self.coords = coords
        self.campaign_coords = coords  # Coordinates of the candidate in the space, used for campaigning
        self.id = id  # Unique identifier for the candidate
        self.approach = approach
        self.votes = 0  # Number of votes received by this candidate
        self.vote_history = []
        self.avg_voter_position = coords  # Average position of voters who voted for this candidate
        self.approach_weight = example_candidate_params.get('approach_weight', 0.1) if params is None else params.get('approach_weight', 0.1)  # Weight of the approach in the candidate's position update

    def __repr__(self):
        return f"Candidate(id={self.id}, coords={self.coords}, votes={self.votes})"


    def update_position(self, target_position: list[float], approach_weight: float = 0.1):
        self.coords[0] += self.approach_weight*(target_position[0] - self.coords[0])
        self.coords[1] += self.approach_weight*(target_position[1] - self.coords[1])
        self.coords = np.clip(self.campaign_coords, 0, 1)

    def make_campaign(self, approach_weight: float = 0.1):
        self.campaign_coords[0] += self.approach_weight*(self.avg_voter_position[0] - self.campaign_coords[0])
        self.campaign_coords[1] += self.approach_weight*(self.avg_voter_position[1] - self.campaign_coords[1])
        self.campaign_coords = np.clip(self.campaign_coords, 0, 1)  # Ensure the coordinates are within the bounds of the space [0, 1] x [0, 1]


class Voter():

    coords: Point  # Coordinates of the voter in the space
    strat : Strategy
    best_preference : float
    worst_tolerance : float
    votes: np.ndarray  # Votes for candidates, indexed by candidate id
    id: int = 0  # Unique identifier for the voter

    def __init__(self, coords: Point, strat : Strategy, parameters: dict, n_candidates : int = 0, id: int = 0):
        self.coords = coords
        self.strat = strat
        self.parameters = parameters if parameters is not None else example_voter_params
        # self.votes = np.ones(n_candidates)/n_candidates # Votes for candidates, given by voting distance based on ideological position and strategy, indexed by candidate id
        self.votes = np.zeros(n_candidates)
        self.parameters = parameters if parameters is not None else example_voter_params
        self.best_preference = self.parameters.get('best_preference', 0.5)  # Best ideological position for the voter
        self.worst_tolerance = self.parameters.get('worst_tolerance', 0.1)  # Worst ideological position that the voter tolerates
        self.id = id  # Unique identifier for the voter

    def update_voting_preferences(self, candidates: list[Candidate], system: System, dist_metric = distance_euclid, polls: list[float] = None, local_neighborhood: list[float] = None, campaigns: list[float] = None):
        self.votes = self.get_votes(candidates, system, polls, dist_metric)
        
        # First Update the votes based on the distance to candidates
        # if all(self.votes == 0) or len(self.votes) == 0:
        #     self.votes = np.array([dist_metric(self.coords, candidate.coords) for candidate in np.random.permutation(candidates)])
        #     # Normalize the votes to probabilities
        #     self.votes = self.votes / np.sum(self.votes)
        # else:
        #     # Update votes based on strategy parameters and polls
        #     for candidate in np.random.permutation(candidates):
        #         self.votes[candidate.id] = dist_metric(self.coords, candidate.coords)  # Distance to candidate's position
        #         # adjust votes based on campaign message - adjusted position of candidate based on polls * campaign_weight
        #         self.votes[candidate.id] -= self.parameters.get('campaign_weight', 0) * 1/ (dist_metric(self.coords, candidate.campaign_coords))
        #         self.votes[candidate.id] -= self.parameters.get('poll_weight', 0) * (polls[candidate.id] if polls is not None else 0)
        #         self.votes[candidate.id] -= self.parameters.get('social_weight', 0) * (local_neighborhood[candidate.id] if local_neighborhood is not None else 0)
        #         self.votes[candidate.id] = max(self.votes[candidate.id], 0)  # Ensure votes are non-negative
        #     # Normalize the votes to probabilities
        #     self.votes = self.votes / np.sum(self.votes)


    # def get_voting_preferences(self):
    #     # honestly returns the index of the candidate with the least distance (most preferred)
    #     return np.argmin(self.votes)

    def get_tolerance(self, best_distance, worst_distance):
        return (self.best_preference* best_distance + self.worst_tolerance * worst_distance) / 2

    # Tolerated candidates, might be empty
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

    def get_votes(self, candidates : list[Candidate], system : System, polls : Optional[list[float]] = None, dist_metric = distance_euclid):
        init_strat = self.strat

        if polls is not None:
            assert len(candidates) == len(polls)
        # If no previous polls exist, ask for honest (or random) opinion
        elif self.strat not in {Strategy.RANDOM, Strategy.HONEST}:
            self.strat = Strategy.HONEST

        votes_counts = [0 for _ in range(len(candidates))]

        match system:

            case System.FPTP | System.INSTANT_RUNOFF: # IR is iterated FPTP

                match self.strat:

                    case Strategy.RANDOM:
                        votes_counts[random.randint(0, len(candidates)-1)] += 1

                    case Strategy.HONEST | Strategy.LOYAL:
                        votes_counts[self.get_voting_preferences()] += 1

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

        # Restore initial strategy
        if polls is None:
            self.strat = init_strat

        return votes_counts


