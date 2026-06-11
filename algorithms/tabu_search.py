import copy
import random

from engine import (
    generate_timetable,
    evaluate_timetable,
    mutate_timetable
)


# ============================================
# TIMETABLE SIGNATURE
# ============================================

def timetable_signature(timetable):
    """Create a hashable signature from course-timeslot pairs."""
    return tuple(
        (entry["course"], entry["timeslot"])
        for entry in timetable
    )


# ============================================
# TABU SEARCH
# ============================================

def run_tabu_search(
    df,
    constraints=None,
    iterations=300,
    tabu_size=30,
    neighbors_count=20
):
    """Run Tabu Search with full constraint support.
    
    constraints: parsed constraint dict from nlp_parser.parse_constraints()
    """

    # INITIAL SOLUTION
    current = generate_timetable(df, constraints)
    current_fitness = evaluate_timetable(current, constraints)["fitness"]

    best = copy.deepcopy(current)
    best_fitness = current_fitness

    history = []

    # TABU LIST
    tabu_list = [timetable_signature(current)]

    # MAIN LOOP
    for iteration in range(iterations):

        neighbors = []

        # GENERATE DIVERSE NEIGHBORS
        for _ in range(neighbors_count):
            neighbor = mutate_timetable(
                copy.deepcopy(current),
                constraints,
                mutation_rate=0.3
            )
            neighbors.append(neighbor)

        best_candidate = None
        best_candidate_fitness = float("inf")

        # SELECT BEST NON-TABU NEIGHBOR
        for neighbor in neighbors:
            signature = timetable_signature(neighbor)

            if signature in tabu_list:
                continue

            fitness = evaluate_timetable(
                neighbor,
                constraints
            )["fitness"]

            if fitness < best_candidate_fitness:
                best_candidate = copy.deepcopy(neighbor)
                best_candidate_fitness = fitness

        # IF ALL ARE TABU — pick best anyway (aspiration)
        if best_candidate is None:
            for neighbor in neighbors:
                fitness = evaluate_timetable(neighbor, constraints)["fitness"]
                if fitness < best_candidate_fitness:
                    best_candidate = copy.deepcopy(neighbor)
                    best_candidate_fitness = fitness

        if best_candidate is None:
            continue

        # MOVE
        current = copy.deepcopy(best_candidate)
        current_fitness = best_candidate_fitness

        # UPDATE BEST
        if current_fitness < best_fitness:
            best = copy.deepcopy(current)
            best_fitness = current_fitness

        # UPDATE TABU LIST
        tabu_list.append(timetable_signature(current))
        if len(tabu_list) > tabu_size:
            tabu_list.pop(0)

        history.append(best_fitness)

        print(f"Tabu Iteration {iteration} | Best Fitness: {best_fitness}")

    return best, best_fitness, history