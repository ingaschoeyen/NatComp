
import EA


class MA(EA.EA):
    def __init__(self, cities, population_size=100, mutation_rate=0.01, crossover_rate=0.7, generations=1000):
        super().__init__(cities, population_size, mutation_rate, crossover_rate, generations)
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generations = generations