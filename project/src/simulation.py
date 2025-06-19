from voter import *
from population import *
from plotting import *
from election import Election
import pandas as pd
from itertools import product
from datetime import datetime
import json
import os
"""Simulation class to run the election simulation with (potentially multiple) populations of voters and candidates."""


example_params = {
    'n_rounds': 10,
    'n_polls': 5,

    }

class Simulation():

    populations: list[Population]
    candidates: list[Population]
    output_sims: dict # DataFrame to store the results of each round


    def __init__(self, population: Population = None, election: Election = None, n_rounds: int = 10, n_polls: int = 5):
        self.population = population if population else Population()
        self.election = election if election else Election()
        self.n_rounds = n_rounds
        self.n_polls = n_polls
        self.output_sims = dict() # {sim_id, sim_results}
        print(f"Simulation initialized with {self.n_rounds} rounds and {self.n_polls} polls per round.")

    def dump_results(self, sim_id):
        # create json_file with sim_id
        file_name = sim_id + '.json'
        json_file_path = os.path.join(os.getcwd(), file_name)

        with open(json_file_path, 'w') as f:
            json.dump(self.output_sims, f)
        print('results dumped')

    def run_election_cycles(self):
        # set up like this so that we can run multiple simulations with different parameters and store results in one json file
        # create unique sim id
        sim_id = str(datetime.now()) + str(np.random.randint(0, 1000000))
        sim_id = sim_id.replace(" ", "_").replace(":", "-").replace(".", "-")  # replace spaces and colons with underscores and hyphens
        self.output_sims['sim_id'] = sim_id
        self.output_sims['results'] = []  # Initialize results list
        output = [{'round': 0, 'votes': [], 'vse': 0.0}]  # Initialize output structure
        
        population = self.population if self.population else Population()
        election = self.election if self.election else Election()
        for rounds in range(self.n_rounds):
            print(f"Running round {rounds + 1}/{self.n_rounds}")
            # Update voter preferences based on candidates
            population.update_voters()
            for i in range(self.n_polls):
                # missing campaigning functionality
                polls, avg_voter_pos = population.polls()
                population.update_voters(polls=polls)
                population.update_candidates(avg_voter_position=avg_voter_pos)
            # do an election
            votes_counts, results, vse = election.do_an_election(population.get_voters(), candidates=population.cands, polls = polls)
            # store results
            election.plot_an_election(population.voters, population.cands, votes_counts, results, output_path=f"./election_round_{rounds + 1}.png")
            self.output_sims.get('results').append({'round': rounds, 'votes': results, 'vse': vse})


        print("Election simulation completed.")
        self.dump_results(sim_id) 

       
    
if __name__ == "__main__":
        population = Population()
        voter_strategies, candidate_approaches = population.get_strategies()
        plot_population(voter_strategies, candidate_approaches, output_path="./population_distribution.png")
        sim = Simulation(population=population, n_rounds=10)
        sim.run_election_cycles()
        plot_sim_dynamics(sim.output_sims.get('results'), output_path="./simulation_dynamics.png")
