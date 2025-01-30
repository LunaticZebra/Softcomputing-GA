import csv
import helper
from GA import GA
from helper import read_cnf_file

# Define a function to test different parameters and log the results to a CSV file


def test_algorithm(filepath, output_csv):
    # Load the CNF file
    clauses, num_variables, num_clauses = read_cnf_file(filepath)

    # Parameter ranges to test
    population_sizes = [8, 16, 32]  # Base population sizes
    evals_before_pop_increases = [8]  # Evaluations before increasing population
    tournament_sizes = [0.1, 0.2]  # Tournament selection size as a fraction of population
    generations = [50, 100]  # Iterations per exchange
    mutation_rates = [0.01, 0.05, 0.1]  # Mutation chances
    crossover_rates = [0.7, 0.8, 0.9]  # Crossover chances
    crossovers = [helper.uniform_crossover, helper.one_point_crossover, helper.two_point_crossover]
    uses_fihc = [False, True]
    num_of_repeats = 10

    num_of_parameters = (len(population_sizes) * len(evals_before_pop_increases) * len(tournament_sizes) *
                         len(generations) * len(mutation_rates) *
                         len(crossover_rates) * len(uses_fihc)) * len(crossovers)

    # Prepare the CSV file for results
    with open(output_csv, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Write the header row
        writer.writerow([
            "Population Size", "Evals Before Pop Increase", "Tournament Size", 
            "Generations", "Mutation Rate", "Crossover Rate", "Crossover type"
            "Best Fitness", "Iterations Taken", "FIHC", "% of time all clauses were satisfied"
        ])

        counter = 0

        # Iterate over all combinations of parameters
        for pop_size in population_sizes:
            for eval_increase in evals_before_pop_increases:
                for t_size in tournament_sizes:
                    for gen in generations:
                        for mut_rate in mutation_rates:
                            for cross_rate in crossover_rates:
                                for fihc in uses_fihc:
                                # Initialize the GA instance with current parameters
                                    for crossover in crossovers:

                                        total_fitness, total_time_taken, clauses_satisfied = 0, 0, 0
                                        for i in range(num_of_repeats):

                                            ga = GA(
                                                pop_size,  # Base population size
                                                eval_increase,  # Evals before population increase
                                                gen,  # Generations (iterations per exchange)
                                                t_size,  # Tournament size
                                                cross_rate,  # Crossover chance
                                                mut_rate,  # Mutation chance
                                                helper.two_point_crossover,  # Crossover function
                                                helper.bit_flip,  # Mutation function
                                                240,  # No improvement iterations (fixed)
                                                num_variables,  # Number of variables
                                                num_clauses,  # Number of clauses
                                                clauses,  # The clauses from the CNF file
                                                quiet=True, # Don't print progress
                                                use_fihc= fihc  # Use First Iteration Hill Climber
                                            )

                                            # Run the algorithm and measure performance
                                            best_fitness, time_taken = ga.run_algorithm()
                                            clauses_satisfied += 1 if num_clauses == best_fitness else 0
                                            total_fitness += best_fitness
                                            total_time_taken += time_taken

                                        total_time_taken /= num_of_repeats
                                        total_fitness /= num_of_repeats
                                        clauses_satisfied /= round(num_of_repeats, 2)
                                        # Write the results to the CSV file
                                        writer.writerow([
                                            pop_size, eval_increase, t_size, gen,
                                            mut_rate, cross_rate, crossover.__name__, total_fitness, total_time_taken, fihc, clauses_satisfied * 100
                                        ])
                                        counter += 1
                                        print(round((counter / num_of_parameters) * 100, 2), "% done")

if __name__ == '__main__':
    # Input CNF file path
    filepath = "data/uf20-01.cnf"
    # Output CSV file path
    output_csv = "algorithm_test_results_20-01.csv"

    # Run the testing function
    test_algorithm(filepath, output_csv)
    print(f"Testing complete. Results saved to {output_csv}")
