from voter import *
from population import *
from plotting import *
from election import Election
import pandas as pd
from itertools import product
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
        self.output_sims = pd.DataFrame(columns=['sim_id', 'rounds', 'votes', 'vse'])
        print(f"Simulation initialized with {self.n_rounds} rounds and {self.n_polls} polls per round.")

    def run_election_cycles(self):
        # create unique sim id
        sim_id = np.random.randint(0, 1000000)
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
            results, vse = election.do_an_election(population.get_voters(), candidates=population.cands, polls = polls)
            # store results
            output = pd.DataFrame({'sim_id': sim_id,
                                   'rounds': rounds,
                                   'votes': results,
                                   'vse': vse})
            pd.concat([self.output_sims, output])

        print("Election simulation completed.")
   
    
if __name__ == "__main__":
        population = Population()
        sim = Simulation(population=population, n_rounds=10)
        sim.run_election_cycles()
        print(sim.output_sims)