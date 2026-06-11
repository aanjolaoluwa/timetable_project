import random
import copy

from engine import (
    generate_timetable,
    evaluate_timetable,
    mutate_timetable,
    crossover_timetable
)


# ============================================
# CROSSOVER
# ============================================

def crossover(parent1, parent2):
    """Single-point crossover between two timetables."""
    size = len(parent1)
    if size <= 2:
        return copy.deepcopy(parent1)
    point = random.randint(1, size - 2)

    child = []
    for i in range(size):
        if i < point:
            child.append(copy.deepcopy(parent1[i]))
        else:
            child.append(copy.deepcopy(parent2[i]))
    return child


# ============================================
# TOURNAMENT SELECTION
# ============================================

def tournament_selection(scored_population, tournament_size=5):
    """Select the best individual from a random tournament."""
    k = min(tournament_size, len(scored_population))
    participants = random.sample(scored_population, k)
    participants.sort(key=lambda x: x[0])
    return participants[0][1]


# ============================================
# GENETIC ALGORITHM
# ============================================

def run_genetic_algorithm(
    df,
    constraints=None,
    population_size=50,
    generations=200,
    mutation_rate=0.2
):
    """Run the Genetic Algorithm with full constraint support.
    
    constraints: parsed constraint dict from nlp_parser.parse_constraints()
                 — used in both initial generation AND fitness evaluation.
    """

    # INITIAL POPULATION — each individual is independently generated
    population = [
        generate_timetable(df, constraints)
        for _ in range(population_size)
    ]

    best_solution = None
    best_fitness = float("inf")
    history = []

    # GENERATIONS LOOP
    for generation in range(generations):

        scored_population = []

        # EVALUATION — constraints applied in fitness scoring
        for timetable in population:
            fitness = evaluate_timetable(
                timetable,
                constraints
            )["fitness"]
            scored_population.append((fitness, timetable))

        scored_population.sort(key=lambda x: x[0])

        current_best_fitness = scored_population[0][0]
        current_best_solution = scored_population[0][1]

        # UPDATE BEST
        if current_best_fitness < best_fitness:
            best_fitness = current_best_fitness
            best_solution = copy.deepcopy(current_best_solution)

        history.append(best_fitness)

        print(f"Generation {generation} | Best Fitness: {best_fitness}")

        # NEW POPULATION
        new_population = []

        # ELITISM — preserve top 5
        elites = [copy.deepcopy(x[1]) for x in scored_population[:5]]
        new_population.extend(elites)

        # OFFSPRING via crossover + mutation
        while len(new_population) < population_size:

            parent1 = tournament_selection(scored_population)
            parent2 = tournament_selection(scored_population)

            child = crossover(parent1, parent2)

            # Mutate with constraints so offspring respect scheduling rules
            child = mutate_timetable(child, constraints, mutation_rate)

            new_population.append(child)

        population = new_population

    return best_solution, best_fitness, history