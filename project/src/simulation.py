from voter import *
from population import *
from plotting import *
from election import Election
import pandas as pd
from itertools import product
from datetime import datetime
import json
import os
import copy
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

    def run_election_cycles(self, save_results: bool = True, plot_results: bool = True, make_gif: bool = False):
        # set up like this so that we can run multiple simulations with different parameters and store results in one json file
        # create unique sim id
        sim_id = str(datetime.now()) + str(np.random.randint(0, 1000000))
        sim_id = sim_id.replace(" ", "_").replace(":", "-").replace(".", "-")  # replace spaces and colons with underscores and hyphens
        self.output_sims['sim_id'] = sim_id
        self.output_sims['results'] = []  # Initialize results list
        output = [{'round': 0, 'votes': [], 'vse_util': 1.0, 'vse_comp': 1.0, 'vse_vdist_comp': 1.0, 'norm_entropy': 1.0}]  # Initialize output structure
        
        population = self.population if self.population else Population()
        election = self.election if self.election else Election()
        results = None
        gif_frames = []  # Store frames for GIF if needed
        for rounds in range(self.n_rounds):
            print(f"Running round {rounds + 1}/{self.n_rounds}")
            # Update voter and candidate positions based on last rounds results

            population.update_voters()
            for i in range(self.n_polls):
                polls, avg_voter_pos = population.polls()
                population.campaign(avg_voter_position=avg_voter_pos, polls=polls)
                population.update_voter_opinions(polls=polls)

            # do an election
            votes_counts, results, vse_util, vse_comp, vse_vdist_comp, norm_entropy = election.do_an_election(population.get_voters(), candidates=population.cands, polls = polls)
            # candidates update based on election
            population.update_candidates(results)

            # store results
            if plot_results:
                election.plot_an_election(population.voters, population.cands, votes_counts, results, output_path=f"./election_round_{rounds + 1}.png")
            self.output_sims.get('results').append({'round': rounds,'votes_count': votes_counts, 'votes_per': results, 'vse_util': vse_util, 'vse_comp': vse_comp, 'vse_vdist_comp': vse_vdist_comp, 'norm_entropy': norm_entropy})
            if make_gif:
                fig, frame_path = get_gif_scatter(population.voters, population.cands, polls, results, election.system, rounds, vse_util,  output_path=f"./election_round_{rounds + 1}_scatter.png")
                fig.show()
                gif_frames.append(frame_path)

        print("Election simulation completed.")

        if make_gif:
            make_gif_scatter(gif_frames, output_path=f"./election_{sim_id}.gif")
        if save_results:
            self.dump_results(sim_id) 
        else:
            return self.output_sims



def run_multiple_voting_systems(voting_systems: list[System], population: Population, n_rounds: int = 10, n_polls: int = 5):
    """
    Run the election simulation for multiple voting systems.
    :param voting_systems: List of voting systems to simulate.
    :param population: Population of voters and candidates.
    :param n_rounds: Number of rounds to run the simulation.
    :param n_polls: Number of polls per round.
    """
    for system in voting_systems:
        print(f"Running simulation for {system.name} voting system.")
        sim = Simulation(population=population.deepcopy(), election=Election(system=system))
        sim.run_election_cycles()
        print(f"Simulation for {system.name} completed.")

       
    
if __name__ == "__main__":
        n_sims = 10
        n_rounds = 30
        system = System.APPROVAL  # Example system, can be changed to any other system
        total_output = []
        population = Population()
        voter_strategies, candidate_approaches = population.get_strategies()
        plot_population(voter_strategies, candidate_approaches, output_path=f"./population_distribution_{system.name}.png")
         
        for i in range(n_sims):
            sim = Simulation(population=copy.copy(population), n_rounds=n_rounds, election=Election(system=system))
            output = sim.run_election_cycles(save_results=False, plot_results=False, make_gif=True)
            plot_sim_dynamics(sim.output_sims.get('results'), output_path=f"./simulation_dynamics_sim{i}_{system.name}.png")
            total_output.append(output)