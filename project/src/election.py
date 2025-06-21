from typing import Any, Dict
from population import Population
from geometry import *
import numpy as np
from enum import Enum
from agents import Voter, Candidate, System
from voting import *
from plotting import plot_closest, plot_approved, plot_bar, plot_pie


default_elect_params = {
    "system": System.FPTP,          # Election system: "fptp", "approval_rel", "instant_runoff", "stv"
    "threshold": 0.1,               # Threshold for the minimum percentage of votes required for a candidate to be considered
    "dist_metric": distance_euclid  # Distance metric to use for calculating distances between voters and candidates
}

class Election():

    def __init__(self, population: Population, params: Dict[str, Any] = None):
        self.population = population
        self.system = params.get('system', default_elect_params['system'])
        self.threshold = params.get('threshold', default_elect_params['threshold'])
        self.dist_metric = params.get('dist_metric', default_elect_params['dist_metric'])

    def get_results(self, polls: list[float]):
        match self.system:
            case System.FPTP:
                return fptp(self.population.voters, self.population.candidates, polls=polls, threshold=self.threshold, dist_metric=self.dist_metric)
            case System.INSTANT_RUNOFF:
                return instant_runoff(self.population.voters, self.population.candidates, polls=polls, threshold=self.threshold, dist_metric=self.dist_metric)
            case System.APPROVAL:
                return approval(self.population.voters, self.population.candidates, polls=polls, threshold=self.threshold, dist_metric=self.dist_metric)

        assert False

    def run_election(self, polls: list[float] = None):
        votes_counts = self.get_results(polls)
        results = percentage(votes_counts)
        vse_utils = vse_util(self.population.voters, self.population.candidates, results)
        vse_comps = vse_comp(self.population.voters, self.population.candidates, results)
        vse_vdist_comps = vse_vdist_comp(self.population.voters, self.population.candidates, results)
        norm_entropy = compute_norm_entropy(results)
        return votes_counts, results, vse_utils, vse_comps, vse_vdist_comps, norm_entropy

    def plot_election(self, voters: list[Voter], candidates: list[Candidate],
                         votes_counts: list[int], results: list[float], output_path: str = None):
        if output_path is None:
            output_path = f"./election_{self.system.name.lower()}.png"
        plot_closest(voters, candidates, output_path=output_path.replace(".png", "_closest.png"))
        plot_bar(votes_counts, output_path=output_path.replace(".png", "_bar.png"))
        plot_pie(votes_counts, output_path=output_path.replace(".png", "_pie.png"))
        plot_approved(voters, candidates, output_path=output_path.replace(".png", "_approved.png"))
        return output_path
