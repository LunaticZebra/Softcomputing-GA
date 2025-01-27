import helper
from GA import GA
from helper import read_cnf_file

if __name__ == '__main__':
    filepath = "data/uf20-01.cnf"
    clauses, num_variables, num_clauses = read_cnf_file(filepath)

    ga = GA(8, 8, 10, 0.2, 0.8, 0.05,
            helper.two_point_crossover, helper.bit_flip, 240, num_variables, num_clauses, clauses)

    ga.run_algorithm()