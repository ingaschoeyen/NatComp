from typing import Any, Dict
import json
import os
from itertools import product
from datetime import datetime
from agents import *
from population import *
from plotting import *
from election import Election
"""Simulation class to run the election simulation with (potentially multiple) populations of voters and candidates."""


default_sim_params = {
    "n_rounds": 10,
    "n_polls": 5
}

class Simulation():

    populations: list[Population]
    candidates: list[Population]
    output_sims: dict # DataFrame to store the results of each round

    def __init__(self, population: Population, params : Dict[str, Any] = default_sim_params):
        self.population = population
        self.election = Election(population=population, params=params)
        self.n_rounds = params.get('n_rounds', default_sim_params['n_rounds'])
        self.n_polls = params.get('n_polls', default_sim_params['n_polls'])
        self.output_sims = dict() # {sim_id, sim_results}
        print(f"Simulation initialized with {self.n_rounds} rounds and {self.n_polls} polls per round.")

    def dump_results(self, sim_id):
        # create json_file with sim_id
        file_name = sim_id + '.json'
        json_file_path = os.path.join(os.getcwd(), file_name)

        with open(json_file_path, 'w') as f:
            json.dump(self.output_sims, f)
        print('results dumped')

    def run_election_cycles(self, save_results: bool = True, plot_results: bool = True, make_gif: bool = False, delete_frames: bool = True):
        # set up like this so that we can run multiple simulations with different parameters and store results in one json file
        # create unique sim id
        sim_id = str(datetime.now()) + str(np.random.randint(0, 1000000))
        sim_id = sim_id.replace(" ", "_").replace(":", "-").replace(".", "-")  # replace spaces and colons with underscores and hyphens
        self.output_sims['sim_id'] = sim_id
        self.output_sims['results'] = []  # Initialize results list
        output = [{'round': 0, 'votes': [], 'vse_util': 1.0, 'vse_comp': 1.0, 'vse_vdist_comp': 1.0, 'norm_entropy': 1.0}]  # Initialize output structure

        population = self.population
        election = self.election
        results = None
        gif_frames = []  # Store frames for GIF if needed
        # TODO reset polls between election rounds?
        polls = None # Initially no previous polls, let everyone vote honestly/randomly

        for rounds in range(self.n_rounds):
            print(f"Running round {rounds + 1}/{self.n_rounds}")

            # Candidates campaign based on the results of the previous election
            population.campaign_candidates(results)

            # Polling and campaigning between elections
            population.update_voters(election.system)
            for i in range(self.n_polls):
                polls, avg_voter_pos = population.take_poll(system=election.system, last_poll=polls)
                population.campaign_voters(avg_voter_position=avg_voter_pos, polls=polls)
                population.update_voters(system=election.system, polls=polls)

            # Election
            votes_counts, results, vse_util, vse_comp, vse_vdist_comp, norm_entropy = election.run_election(polls=polls)

            # store results
            if plot_results:
                election.plot_election(population.voters, population.candidates, votes_counts, results, output_path=f"./election_round_{rounds + 1}.png")
            self.output_sims.get('results').append({'round': rounds,'votes_count': votes_counts, 'votes_per': results, 'vse_util': vse_util, 'vse_comp': vse_comp, 'vse_vdist_comp': vse_vdist_comp, 'norm_entropy': norm_entropy})
            if make_gif:
                fig, frame_path = get_gif_scatter(population.voters, population.candidates, polls, results, election.system, rounds, vse_util, output_path=f"./election_round_{rounds + 1}_scatter.png")
                fig.show()
                gif_frames.append(frame_path)

        print("Election simulation completed.")

        if make_gif:
            make_gif_scatter(gif_frames, output_path=f"./election_{sim_id}.gif", delete_frames=delete_frames)
        if save_results:
            self.dump_results(sim_id)
        else:
            return self.output_sims

def run_multiple_voting_systems(voting_systems: list[System], population: Population, params : Dict[str, Any] = default_sim_params):
    """
    Run the election simulation for multiple voting systems.
    :param voting_systems: List of voting systems to simulate.
    :param population: Population of voters and candidates.
    :param n_rounds: Number of rounds to run the simulation.
    :param n_polls: Number of polls per round.
    """
    for system in voting_systems:
        print(f"Running simulation for {system.name} voting system.")
        sim = Simulation(population=population.deepcopy(), election=Election(population=population, params=params))
        sim.run_election_cycles()
        print(f"Simulation for {system.name} completed.")
