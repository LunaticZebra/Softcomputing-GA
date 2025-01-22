import random


def read_cnf_file(file_name: str):
    clauses = []
    num_variables = 0
    num_clauses = 0

    with open(file_name,'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line.startswith('c') or not line:
                continue
            # Problem description line
            if line.startswith('p'):
                _,_,num_variables,num_clauses = line.split()
                num_variables,num_clauses = int(num_variables),int(num_clauses)
            # Clause line
            else:
                clause = [int(x) for x in line.split() if x != '0']
                clauses.append(clause)

    print(f"File processed: {file_name}, number of variables: {num_variables}, number of clauses: {num_clauses}")

    return clauses, num_variables, num_clauses

def evaluate_formula(clauses, assignment: list[bool]):

    number_of_satisfied_clauses = 0

    for clause in clauses:

        for literal in clause:
            var = abs(literal)

            value = assignment[var]

            # Negated literal
            if literal < 0:
                value = not value

            if value:
                number_of_satisfied_clauses += 1
                break

    return number_of_satisfied_clauses


def one_point_crossover(parent1, parent2):
    assert len(parent1) == len(parent2)

    crossover_point = random.randint(1, len(parent1) - 1)

    # Swap the segments after the crossover point
    offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
    offspring2 = parent2[:crossover_point] + parent1[crossover_point:]

    return offspring1, offspring2


def two_point_crossover(parent1, parent2):
    assert len(parent1) == len(parent2)

    crossover_point1 = random.randint(1, len(parent1) - 2)
    crossover_point2 = random.randint(crossover_point1 + 1, len(parent1) - 1)

    # Swap the segments between the points
    offspring1 = parent1[:crossover_point1] + parent2[crossover_point1:crossover_point2] + parent1[crossover_point2:]
    offspring2 = parent2[:crossover_point1] + parent1[crossover_point1:crossover_point2] + parent2[crossover_point2:]

    return offspring1, offspring2


def uniform_crossover(parent1, parent2):
    assert len(parent1) == len(parent2)

    offspring1 = []
    offspring2 = []

    for gene1, gene2 in zip(parent1, parent2):
        if random.random() < 0.5:
            offspring1.append(gene1)
            offspring2.append(gene2)
        else:
            offspring1.append(gene2)
            offspring2.append(gene1)

    return offspring1, offspring2

def bit_flip(chromosome, gene):
    chromosome.genes[gene] = not chromosome.genes[gene]