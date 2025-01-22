import math
import random
from typing import Callable

import helper
from Chromosome import Chromosome


class GA:

    def __init__(self,base_population_size: int,evals_before_pop_increase: int,
                 tournament_size: float,num_of_iterations: int,crossover_chance: float,  mutation_chance: float,
                 crossover_function: Callable[[tuple[list[int]]], list[int]],
                 mutation_function: Callable[[list[int]], list[int]],
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

        self.clauses = clauses
        self.variables_num = variables_num
        self.clauses_num = clauses_num

        self.populations = {}
        self.evaluated_chromosomes = {}
        self.current_pop_power = 1


    def run_tournament(self, pop_pow):
        population = self.populations[pop_pow]
        tournament_size = math.floor(self.t_size * len(population))

        tournament_contestants = random.sample(population, tournament_size)

        best_chromosome = tournament_contestants[0]
        best_fitness = tournament_contestants[0].fitness


        for i in range(1, self.num_of_iterations):
            chromosome_fitness = self.evaluated_chromosomes[best_chromosome].fitness
            if chromosome_fitness > best_fitness:
                best_chromosome = tournament_contestants[i]


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
