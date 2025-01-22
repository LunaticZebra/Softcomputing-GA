class Chromosome:
    def __init__(self, genes_sequence: list[bool], fitness = None):
        self.genes = genes_sequence
        self.fitness = fitness

    def __hash__(self):
        return hash(tuple(self.genes))