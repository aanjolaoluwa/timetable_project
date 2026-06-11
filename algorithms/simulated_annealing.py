import math
import random
import copy

from engine import (
    generate_timetable,
    evaluate_timetable,
    mutate_timetable
)


# ============================================
# SIMULATED ANNEALING
# ============================================

def run_simulated_annealing(
    df,
    constraints=None,
    initial_solution=None,
    initial_temperature=10000,
    cooling_rate=0.995,
    iterations=500
):
    """Run Simulated Annealing with full constraint support.
    
    constraints: parsed constraint dict from nlp_parser.parse_constraints()
    """

    # INITIAL SOLUTION
    current = (
        copy.deepcopy(initial_solution)
        if initial_solution
        else generate_timetable(df, constraints)
    )

    current_fitness = evaluate_timetable(current, constraints)["fitness"]

    best = copy.deepcopy(current)
    best_fitness = current_fitness

    temperature = initial_temperature
    history = []

    # MAIN LOOP
    for iteration in range(iterations):

        # NEIGHBOR — mutated with constraint awareness
        neighbor = mutate_timetable(
            copy.deepcopy(current),
            constraints,
            mutation_rate=0.1
        )

        neighbor_fitness = evaluate_timetable(
            neighbor,
            constraints
        )["fitness"]

        delta = neighbor_fitness - current_fitness

        # ACCEPTANCE RULE (accept worse solutions probabilistically)
        if delta < 0 or random.random() < math.exp(-delta / max(temperature, 0.001)):
            current = copy.deepcopy(neighbor)
            current_fitness = neighbor_fitness

        # UPDATE BEST
        if current_fitness < best_fitness:
            best = copy.deepcopy(current)
            best_fitness = current_fitness

        history.append(best_fitness)

        # COOLING
        temperature *= cooling_rate
        if temperature < 0.001:
            temperature = 0.001

        print(f"SA Iteration {iteration} | Best Fitness: {best_fitness}")

    return best, best_fitness, history