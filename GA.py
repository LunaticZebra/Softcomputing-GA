import csv
import math
import random
from typing import Callable

import helper
from Chromosome import Chromosome


class GA:

    def __init__(self, base_population_size: int, evals_before_pop_increase: int, iterations_per_exchange: int,
                 tournament_size: float, crossover_chance: float, mutation_chance: float,
                 crossover_function: Callable[[list[bool], list[bool]], tuple[list[bool], list[bool]]],
                 mutation_function: Callable[[list[bool]], None], no_improvement_iterations: int,
                 variables_num: int, clauses_num: int,
                 clauses: list[list[int]],
                 quiet: bool = False,
                 use_fihc: bool = False):

        self.base_pop_size = base_population_size
        self.evals_before_pop_increase = evals_before_pop_increase
        self.iterations_per_exchange = iterations_per_exchange
        self.t_size = tournament_size
        self.crossover_chance = crossover_chance
        self.mutation_chance = mutation_chance
        self.crossover_function = crossover_function
        self.mutation_function = mutation_function
        self.max_no_improv = no_improvement_iterations
        self.best_chromosomes = {}
        self.quiet = quiet
        self.use_fihc = use_fihc

        self.clauses = clauses
        self.variables_num = variables_num
        self.clauses_num = clauses_num

        self.populations = {}
        self.evaluated_chromosomes = {}
        self.current_max_pop_key = 1

        self.iteration_number = 0

        self.increase_population()

        self.file = open("results.csv", mode="w", newline='')
        self.writer = csv.writer(self.file)
        self.writer.writerow(["Iteration", "Best fitness", "Average Fitness", "Worst Fitness"])

    def run_algorithm(self):

        iteration_tracker = {key: 0 for key in sorted(
            self.populations.keys())}  # Track the amount of iterations for each population, it is important that they are sorted
        iteration_level = 0  # Currently evaluated population
        keys = sorted(list(iteration_tracker.keys()))

        no_improve = 0

        best_chromosome = max(self.best_chromosomes.values(), key=lambda x: x.fitness)

        while no_improve < self.max_no_improv:

            self.iteration_number += 1
            # Because the list of keys is sorted, we choose current population key this way
            current_iteration_key = keys[iteration_level]

            self.iterate(current_iteration_key)

            if self.iteration_number % self.iterations_per_exchange == 0:
                if not self.quiet:
                    print("Exchanging between populations, iteration ", self.iteration_number)
                self.exchange_best_between_populations()
            # Check whether we should go iterate for a population with greater size or go back to level 0
            if iteration_tracker[current_iteration_key] != self.evals_before_pop_increase:

                iteration_tracker[current_iteration_key] += 1
                iteration_level = 0

            else:

                iteration_tracker[current_iteration_key] = 0
                iteration_level += 1

                if iteration_level == len(self.populations):
                    self.trim_populations()
                    self.increase_population()

                    iteration_tracker = {key: 0 for key in sorted(self.populations.keys())}
                    keys = sorted(list(iteration_tracker.keys()))

                    iteration_level = len(self.populations) - 1

            curr_best_chromosome = max(self.best_chromosomes.values(), key=lambda x: x.fitness)

            if self.use_fihc and no_improve == (math.floor(self.max_no_improv * 0.9) - 1):
                self.fihc(self.best_chromosomes[current_iteration_key])

            if curr_best_chromosome.fitness <= best_chromosome.fitness:
                no_improve += 1
            else:
                best_chromosome = curr_best_chromosome
                no_improve = 0

                if best_chromosome.fitness == self.clauses_num:
                    if not self.quiet:
                        print("Found solution")
                    break

            self._write_row(self._get_best_avg_worst_overall_fitness())

        if not self.quiet:
            print(f"Clauses to satisfy = {len(self.clauses)}")
            print(f"Clauses satisfied = {best_chromosome.fitness}")
            print(f"Best chromosome = {best_chromosome.genes}")
            print(self.populations.keys())
        self._close_file()
        return best_chromosome.fitness, self.iteration_number

    def iterate(self, pop_key):

        parent1 = self.run_tournament(pop_key)
        parent2 = self.run_tournament(pop_key)

        while parent1 == parent2:
            parent2 = self.run_tournament(pop_key)

        offspring1 = Chromosome(parent1.genes[:], parent1.fitness)
        offspring2 = Chromosome(parent2.genes[:], parent2.fitness)

        if random.random() < self.crossover_chance:
            offspring1_genes, offspring2_genes = self.crossover_function(parent1.genes, parent2.genes)
            offspring1 = Chromosome(offspring1_genes)
            offspring2 = Chromosome(offspring2_genes)

            self.evaluate_chromosome(offspring1)
            self.evaluate_chromosome(offspring2)

        if random.random() < self.mutation_chance:
            offspring1_mutated_genes, offspring2_mutated_genes = offspring1.genes[:], offspring2.genes[:]
            self.mutation_function(offspring1_mutated_genes)
            self.mutation_function(offspring2_mutated_genes)

            mutated_offspring1 = Chromosome(offspring1_mutated_genes)
            mutated_offspring2 = Chromosome(offspring1_mutated_genes)

            self.evaluate_chromosome(mutated_offspring1)
            self.evaluate_chromosome(mutated_offspring2)

            if offspring1.fitness <= mutated_offspring1.fitness:
                offspring1 = mutated_offspring1
            if offspring2.fitness <= mutated_offspring2.fitness:
                offspring2 = mutated_offspring2

        # replace 2 chromosomes of the lowest fitness with new offspring
        min_chromosome1 = min(self.populations[pop_key], key=lambda x: x.fitness)
        chromosome1_fitness = min_chromosome1.fitness
        min_chromosome1.fitness = math.inf
        min_chromosome2 = min(self.populations[pop_key], key=lambda x: x.fitness)
        min_chromosome1.fitness = chromosome1_fitness

        # possibility -> do not remove chromosomes if they are better than newly created offspring
        if offspring1.fitness > min_chromosome1.fitness:
            self.populations[pop_key].remove(min_chromosome1)
            self.populations[pop_key].append(offspring1)

        if offspring2.fitness > min_chromosome2.fitness:
            self.populations[pop_key].remove(min_chromosome2)
            self.populations[pop_key].append(offspring2)

        self.evaluate_population(pop_key)

    def exchange_best_between_populations(self):
        chromosomes_to_exchange = []

        # Shuffle the keys so their position are different
        while True:
            keys = list(self.populations.keys())
            shuffled = list(keys[:])
            random.shuffle(shuffled)
            # Check if any number remains in its original position
            if all(original != shuffled[i] for i, original in enumerate(keys)):
                break

        # Acquire the best chromosome from each population and remove it from there

        for i in range(len(keys)):
            population = self.populations[keys[i]]
            best_chromosome = self.best_chromosomes[keys[i]]

            population.remove(best_chromosome)

            chromosomes_to_exchange.append(best_chromosome)

        for i in range(len(keys)):
            self.populations[shuffled[i]].append(chromosomes_to_exchange[i])
            self.best_chromosomes[shuffled[i]] = chromosomes_to_exchange[i]

    def run_tournament(self, pop_key: int) -> Chromosome:
        population = self.populations[pop_key]
        tournament_size = math.ceil(self.t_size * len(population))

        tournament_contestants = random.sample(population, tournament_size)

        best_chromosome = tournament_contestants[0]
        best_fitness = tournament_contestants[0].fitness

        for i in range(1, len(tournament_contestants)):
            if tournament_contestants[i].fitness > best_fitness:
                best_chromosome = tournament_contestants[i]

        return best_chromosome

    def increase_population(self):
        population = []
        for i in range(self.base_pop_size * 2 ** self.current_max_pop_key):
            genes_seq = []
            for _ in range(self.variables_num):
                genes_seq.append(random.choice([True, False]))

            chromosome = Chromosome(genes_seq)
            population.append(chromosome)
            self.evaluate_chromosome(chromosome)

        self.populations[self.current_max_pop_key] = population
        self.evaluate_population(self.current_max_pop_key)
        if not self.quiet:
            print(
                f"Iteration: {self.iteration_number}, population of size {len(self.populations[self.current_max_pop_key])} created")
        self.current_max_pop_key += 1

    def evaluate_chromosome(self, chromosome: Chromosome):

        if chromosome not in self.evaluated_chromosomes:
            fitness = helper.evaluate_formula(self.clauses, chromosome.genes)
            self.evaluated_chromosomes[chromosome] = fitness

        else:
            fitness = self.evaluated_chromosomes[chromosome]

        chromosome.fitness = fitness

    def evaluate_population(self, pop_key):
        total_fitness = 0
        best_fitness = 0
        best_chromosome = None
        for chromosome in self.populations[pop_key]:
            if best_fitness < chromosome.fitness:
                best_fitness = chromosome.fitness
                best_chromosome = chromosome
            total_fitness += chromosome.fitness

        self.best_chromosomes[pop_key] = best_chromosome

        return total_fitness, best_fitness

    def trim_populations(self):
        pop_keys = sorted(self.populations.keys())
        pops_to_delete = set()
        for i in range(1, len(pop_keys)):
            curr_pop_fitness, curr_best_fitness = self.evaluate_population(pop_keys[i])
            for j in range(0, i):
                pop_fitness, best_fitness = self.evaluate_population(pop_keys[j])

                if curr_pop_fitness >= pop_fitness and curr_best_fitness >= best_fitness:
                    pops_to_delete.add(pop_keys[j])
                    if not self.quiet:
                        print(f"Trimming population {pop_keys[j]}")

        self.populations = {key: value for key, value in self.populations.items() if key not in pops_to_delete}
        self.best_chromosomes = {key: value for key, value in self.best_chromosomes.items() if
                                 key not in pops_to_delete}

        return pops_to_delete

    def fihc(self, chromosome: Chromosome):

        original_genes = chromosome.genes[:]
        original_chromosome_fitness = chromosome.fitness
        no_improvement = True
        for i in range(self.variables_num):
            chromosome.genes[i] = not chromosome.genes[i]
            self.evaluate_chromosome(chromosome)
            if chromosome.fitness > original_chromosome_fitness:
                no_improvement = False
                break

        if no_improvement:
            chromosome.genes = original_genes
            self.evaluate_chromosome(chromosome)

    def _get_best_avg_worst_overall_fitness(self):
        best_fitness = max(self.best_chromosomes.values(), key=lambda x: x.fitness).fitness
        worst_fitnesses = []
        avg_fitness = 0
        for pop in self.populations.keys():
            worst_fitnesses.append(min(self.populations[pop], key=lambda x: x.fitness).fitness)
            worst_fitnesses.append(min(self.populations[pop], key=lambda x: x.fitness).fitness)
            avg_fitness += (self.evaluate_population(pop)[0]) / len(self.populations[pop])

        avg_fitness /= len(self.populations)
        worst_fitness = min(worst_fitnesses)

        return best_fitness, avg_fitness, worst_fitness

    def _write_row(self, row: tuple[int, int, float]):
        row_to_write = [self.iteration_number, row[0], row[1], row[2]]
        self.writer.writerow(row_to_write)

    def _close_file(self):
        if self.file:
            self.file.close()
