from geometry import *
import numpy as np
from enum import Enum
import random

class System(Enum):
    FPTP = 1
    INSTANT_RUNOFF = 2
    APPROVAL = 3

class Strategy(Enum):
    RANDOM = 1 # Vote randomly
    HONEST = 2 # Vote according to personal preferences, polls have no effect
    POPULIST = 3 # Support most popular candidate, personal preferences have no effect
    REALIST = 4 # Support most popular tolerated candidate, support all tolerated if possible
    LOYAL = 5 # Support favourite candidate, support only non-threatening tolerated candidates

class Candidate():

    coords : Point
    id: int  # Unique identifier for the candidate
    votes: int  # Number of votes received by this candidate
    vote_history: list[int]  # History of votes received by this candidate

    def __init__(self, coords : Point, id : int= 0):
        self.coords = coords
        self.id = id  # Unique identifier for the candidate
        self.votes = 0  # Number of votes received by this candidate
        self.vote_history = []
        self.avg_voter_position = None  # Average position of voters who voted for this candidate

    def __repr__(self):
        return f"Candidate(id={self.id}, coords={self.coords}, votes={self.votes})"

    # TODO: implement methods for campaigning, updating position, etc.
    def update_voters(self, voters = None):
        if self.avg_voter_position is None:
            self.avg_voter_position = self.coords
        else:
            avg_x = sum(x.coords[0] for x in voters)  # Euclidean distance
            avg_y = sum(x.coords[1] for x in voters)  # Euclidean distance
            self.avg_voter_position = [avg_x / len(voters), avg_y / len(voters)]

    def update_position(self, new_coords: list[float]):
        self.coords = new_coords

class Voter():

    coords: list[float]  # Coordinates of the voter in the space
    strat : Strategy
    best_preference : float
    worst_tolerance : float
    votes: np.ndarray  # Votes for candidates, indexed by candidate id

    def __init__(self, coords : Point, strat : Strategy, best_preference : float, worst_tolerance : float,
                 n_candidates : int = 0, parameters: dict = None):
        self.coords = coords
        self.strat = strat
        self.best_preference = best_preference
        self.worst_tolerance = worst_tolerance
        self.votes = np.zeros(n_candidates) # Votes for candidates, given by voting distance based on ideological position and strategy, indexed by candidate id
        self.parameters = parameters if parameters is not None else {}

    def update_voting_preferences(self, candidates: list[Candidate], dist_metric = distance_euclid, polls: list[float] = None, local_neighborhood: list[float] = None, campaigns: list[float] = None):
        # First Update the votes based on the distance to candidates
        if all(self.votes == 0):
            self.votes = np.array([dist_metric(self.coords, candidate.coords) for candidate in candidates])
            # Normalize the votes to probabilities
            self.votes = self.votes / np.sum(self.votes)
        else:
            # Update votes based on strategy parameters and polls
            for i, candidate in enumerate(candidates):
                # Calculate the distance to the candidate
                self.votes[i] = dist_metric(self.coords, candidate.coords)
                # adjust votes based on campaign message - adjusted position of candidate based on polls * campaign_weight
                self.votes[i] -= self.parameters.get('campaign_weight', 0) * (dist_metric(self.coords, campaigns[i] if campaigns is not None else candidate.coords))
                self.votes[i] -= self.parameters.get('poll_weight', 0) * (polls[i] if polls is not None else 0)
                self.votes[i] -= self.parameters.get('social_weight', 0) * (local_neighborhood[i] if local_neighborhood is not None else 0)
            # Normalize the votes to probabilities
            self.votes = self.votes / np.sum(self.votes)

    def get_voting_preferences(self):
        # honestly returns the index of the candidate with the least distance (most preferred)
        return np.argmin(self.votes)

    def get_tolerance(self, best_distance, worst_distance):
        return (self.best_preference * best_distance + self.worst_tolerance * worst_distance) / 2

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
