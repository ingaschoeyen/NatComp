from geometry import *
import numpy as np

class Candidate():

    coords: list[float]  # Coordinates of the candidate in the space
    id: int  # Unique identifier for the candidate
    votes: int  # Number of votes received by this candidate
    vote_history: list[int]  # History of votes received by this candidate

    def __init__(self, coords: list[float], id: int):
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
    votes: np.ndarray  # Votes for candidates, indexed by candidate id

    def __init__(self, coords: list[float], n_candidates : int, parameters: dict = None):

        self.coords = coords
        self.votes = np.zeros(n_candidates) # Votes for candidates, given by voting distance based on ideological position and strategy, indexed by candidate id
        self.parameters = parameters if parameters is not None else {}

    def updateVotingPreferences(self, candidates: list[Candidate], dist_metric = distance_euclid, polls: list[float] = None, local_neighborhood: list[float] = None, campaigns: list[float] = None):
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
    
    def getVotingPreferences(self):
        # honestly returns the index of the candidate with the least distance (most preferred)
        return np.argmin(self.votes)