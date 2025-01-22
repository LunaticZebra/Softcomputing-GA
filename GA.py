import math
import random
from typing import Callable

import helper
from Chromosome import Chromosome


class GA:

    def __init__(self,base_population_size: int,evals_before_pop_increase: int,
                 tournament_size: float,num_of_iterations: int,crossover_chance: float,  mutation_chance: float,
                 keep_m_best:int, replacement_rate: float,
                 crossover_function: Callable[[list[int], list[int]], tuple[list[int], list[int]]],
                 mutation_function: Callable[[list[int]], None],
                 variables_num: int, clauses_num: int,
                 clauses: list[list[int]]):

        self.base_pop_size = base_population_size
        self.evals_before_pop_increase = evals_before_pop_increase
        self.t_size = tournament_size
        self.num_of_iterations = num_of_iterations
        self.crossover_chance = crossover_chance
        self.mutation_chance = mutation_chance
        self.crossover_function = crossover_function
        self.mutation_function = mutation_function
        self.elitism = keep_m_best
        self.replacement_rate = replacement_rate

        self.clauses = clauses
        self.variables_num = variables_num
        self.clauses_num = clauses_num

        self.populations = {}
        self.evaluated_chromosomes = {}
        self.current_pop_power = 1

        self.increase_population()


    def run_algorithm(self):

        iteration_tracker = {key: 0 for key in sorted(self.populations.keys())} # Track the amount of iterations for each population, it is important that they are sorted
        iteration_level = 0 # Currently evaluated population
        keys = list(iteration_tracker.keys())
        print(keys)

        while True:

            if iteration_tracker[iteration_level] != self.evals_before_pop_increase:

                iteration_tracker[iteration_level] += 1
                iteration_level = 0

            else:

                iteration_tracker[iteration_level] = 0
                iteration_level += 1

                self.trim_populations()
                if iteration_level == len(self.populations):
                    self.increase_population()

                iteration_tracker = {key: 0 for key in sorted(self.populations.keys())}
                keys = list(iteration_tracker.keys())


    def iterate(self, pop_key):
        for i in range(self.evals_before_pop_increase):

            parent1 = self.run_tournament(pop_key)
            parent2 = self.run_tournament(pop_key)

            while parent1 == parent2:
                parent2 = self.run_tournament(pop_key)

            offspring1,offspring2 = parent1,parent2
            if random.random() < self.crossover_chance:
                offspring1,offspring2 = self.crossover_function(parent1.genes,parent2.genes)

            if random.random() < self.mutation_chance:
                self.mutation_function(offspring1.genes)
                self.mutation_function(offspring2.genes)

            self.populations[pop_key][-2] = [offspring1,offspring2]


    def exchange_best_between_populations(self):
        best_chromosomes = []
        while True:
            keys = list(self.populations.keys())
            shuffled = list(keys[:])
            random.shuffle(shuffled)
            # Check if any number remains in its original position
            if all(original != shuffled[i] for i,original in enumerate(keys)):
                break

        # Acquire the best chromosome from each population and remove it from there
        for i in range(len(keys)):
            population = self.populations[keys[i]]
            best_chromosome = max(population, key=lambda x: x.fitness)
            population.remove(best_chromosome)
            best_chromosomes.append(best_chromosome)

        # Add the chromosomes accordingly to different populations
        for i in range(len(keys)):
            self.populations[shuffled[i]].append(best_chromosomes[i])

    def run_tournament(self, pop_key: int) -> Chromosome:
        population = self.populations[pop_key]
        tournament_size = math.floor(self.t_size * len(population))

        tournament_contestants = random.sample(population, tournament_size)

        best_chromosome = tournament_contestants[0]
        best_fitness = tournament_contestants[0].fitness


        for i in range(1, self.num_of_iterations):
            chromosome_fitness = self.evaluated_chromosomes[best_chromosome].fitness
            if chromosome_fitness > best_fitness:
                best_chromosome = tournament_contestants[i]

        return best_chromosome

    def increase_population(self):
        population = []
        for i in range(self.base_pop_size**self.current_pop_power):
            genes_seq = []
            for _ in range(self.variables_num):
                genes_seq.append(random.choice([True, False]))

            chromosome = Chromosome(genes_seq)
            population.append(chromosome)
            self.evaluate_chromosome(chromosome)

        self.populations[self.current_pop_power] = population
        self.current_pop_power += 1

    def evaluate_chromosome(self, chromosome: Chromosome):

        fitness = helper.evaluate_formula(self.clauses, chromosome.genes)
        chromosome.fitness = fitness
        self.evaluated_chromosomes[chromosome] = fitness


    def evaluate_population(self, pop_power):
        total_fitness = 0
        best_fitness = 0
        for chromosome in self.populations[pop_power]:
            if best_fitness < chromosome.fitness:
                best_fitness = chromosome.fitness
            total_fitness += chromosome.fitness
        return total_fitness, best_fitness


    def trim_populations(self):
        pop_powers = sorted(self.populations.keys())
        pops_to_delete = set()
        for i in range(1, len(pop_powers)):
            curr_pop_fitness, curr_best_fitness = self.evaluate_population(pop_powers[i])
            for j in range(0, i):
                pop_fitness, best_fitness = self.evaluate_population(pop_powers[j])

                if curr_pop_fitness >= pop_fitness and curr_best_fitness >= best_fitness:
                    pops_to_delete.add(pop_powers[j])

        self.populations = {key: value for key,value in self.populations.items() if key not in pops_to_delete}

        return pops_to_delete