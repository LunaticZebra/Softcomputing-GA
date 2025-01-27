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

            # End character that means the end of file
            elif line.startswith('%'):
                break

            # Problem description line
            elif line.startswith('p'):
                _,_,num_variables,num_clauses = line.split()
                num_variables,num_clauses = int(num_variables),int(num_clauses)

            # Clause line
            else:
                clause = [int(x) for x in line.split() if x != '0']
                clauses.append(clause)


    return clauses, num_variables, num_clauses

def evaluate_formula(clauses, assignment: list[bool]):

    number_of_satisfied_clauses = 0

    for clause in clauses:

        for literal in clause:
            # Take abs value and include offset because of index starts from 0 not 1
            var = abs(literal) - 1

            value = assignment[var]

            # Negated literal
            if literal < 0:
                value = not value

            if value:
                number_of_satisfied_clauses += 1
                break

    return number_of_satisfied_clauses


def one_point_crossover(parent1, parent2) -> tuple[list[bool], list[bool]]:
    assert len(parent1) == len(parent2)

    crossover_point = random.randint(1, len(parent1) - 1)

    # Swap the segments after the crossover point
    offspring1 = parent1[:crossover_point] + parent2[crossover_point:]
    offspring2 = parent2[:crossover_point] + parent1[crossover_point:]

    return offspring1, offspring2


def two_point_crossover(parent1, parent2) -> tuple[list[bool], list[bool]]:
    assert len(parent1) == len(parent2)

    crossover_point1 = random.randint(1, len(parent1) - 2)
    crossover_point2 = random.randint(crossover_point1 + 1, len(parent1) - 1)

    # Swap the segments between the points
    offspring1 = parent1[:crossover_point1] + parent2[crossover_point1:crossover_point2] + parent1[crossover_point2:]
    offspring2 = parent2[:crossover_point1] + parent1[crossover_point1:crossover_point2] + parent2[crossover_point2:]

    return offspring1, offspring2


def uniform_crossover(parent1, parent2) -> tuple[list[bool], list[bool]]:
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

def bit_flip(genes_sequence):
    gene = random.randint(0, len(genes_sequence) - 1)
    genes_sequence[gene] = not genes_sequence[gene]
