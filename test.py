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
    evals_before_pop_increases = [8, 16, 32]  # Evaluations before increasing population
    tournament_sizes = [0.2, 0.5, 0.8]  # Tournament selection size as a fraction of population
    generations = [100, 200, 300]  # Iterations per exchange
    mutation_rates = [0.01, 0.05, 0.1]  # Mutation chances
    crossover_rates = [0.6, 0.8, 0.9]  # Crossover chances

    # Prepare the CSV file for results
    with open(output_csv, mode='w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        # Write the header row
        writer.writerow([
            "Population Size", "Evals Before Pop Increase", "Tournament Size", 
            "Generations", "Mutation Rate", "Crossover Rate", 
            "Best Fitness", "Iterations Taken"
        ])

        # Iterate over all combinations of parameters
        for pop_size in population_sizes:
            for eval_increase in evals_before_pop_increases:
                for t_size in tournament_sizes:
                    for gen in generations:
                        for mut_rate in mutation_rates:
                            for cross_rate in crossover_rates:
                                # Initialize the GA instance with current parameters
                                ga = GA(
                                    pop_size,                # Base population size
                                    eval_increase,           # Evals before population increase
                                    gen,                     # Generations (iterations per exchange)
                                    t_size,                  # Tournament size
                                    cross_rate,              # Crossover chance
                                    mut_rate,                # Mutation chance
                                    helper.two_point_crossover,  # Crossover function
                                    helper.bit_flip,         # Mutation function
                                    240,                     # No improvement iterations (fixed)
                                    num_variables,           # Number of variables
                                    num_clauses,             # Number of clauses
                                    clauses,                  # The clauses from the CNF file
                                    quiet=True                # Don't print progress
                                )

                                # Run the algorithm and measure performance
                                best_fitness, time_taken = ga.run_algorithm()

                                # Write the results to the CSV file
                                writer.writerow([
                                    pop_size, eval_increase, t_size, gen, 
                                    mut_rate, cross_rate, best_fitness, time_taken
                                ])

if __name__ == '__main__':
    # Input CNF file path
    filepath = "data/uf20-01.cnf"
    # Output CSV file path
    output_csv = "algorithm_test_results.csv"

    # Run the testing function
    test_algorithm(filepath, output_csv)
    print(f"Testing complete. Results saved to {output_csv}")
