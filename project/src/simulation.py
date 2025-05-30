from voter import *
from population import *
from plotting import *

import pandas as pd
from itertools import product
"""Simulation class to run the election simulation with (potentially multiple) populations of voters and candidates."""


example_params = {
    'n_rounds': 10,
    'n_polls': 5,

    }

class Simulation:

    population: list[Population]
    candidates: list[Population]
    output: pd.DataFrame  # DataFrame to store the results of each round


    def __init(self, population: Population, candidates: list[Candidate], n_rounds: int = 10):
        self.population = population
        self.candidates = candidates
        self.n_rounds = n_rounds
        self.output = pd.DataFrame(columns=['round', 'candidate_id', 'votes', 'avg_voter_position'])

    def run_election_cycles(self, population: Population = None, candidates: Population = None):
        population = population if population else self.population[0]
        candidates = candidates if candidates else self.candidates[0]
        for rounds in range(self.n_rounds):
            print(f"Running round {rounds + 1}/{self.n_rounds}")
            # Update voter preferences based on candidates
            population.update_voters(candidates)
            for i in range(self.n_polls):
                # missing campaigning functionality
                polls, avg_voter_pos = population.polls(candidates=candidates)
                population.update_votiers(candidates, polls=polls, avg_voter_pos=avg_voter_pos)
                candidates.update_candidates(avg_voter_pos=avg_voter_pos, polls=polls)
            # do an election
            

        print("Election simulation completed.")
        return self.output
    

    def run_multiple_populations(self, populations: list[Population], candidates: list[Candidate], n_rounds: int = 10):
        self.output = pd.DataFrame(columns=['round', 'population_id', 'candidate_id', 'votes', 'avg_voter_position'])
        combs = product(populations, candidates)
        for population, candidates in combs:
            print(f"Running election for population {population.id}")
            result = self.run_election_cycles(population=population, candidates=candidates)

            # Append results to the output DataFrame
            for index, row in result.iterrows():
                self.output = self.output.append({
                    'round': row['round'],
                    'population_id': population.id,
                    'candidate_id': row['candidate_id'],
                    'votes': row['votes'],
                    'avg_voter_position': row['avg_voter_position']
                }, ignore_index=True)

        print("All populations have been processed.")
        return self.output