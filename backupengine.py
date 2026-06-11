import pandas as pd
import time

from engine import generate_timetable, evaluate_timetable

from algorithms.genetic_algorithm import run_genetic_algorithm
from algorithms.simulated_annealing import run_simulated_annealing
from algorithms.tabu_search import run_tabu_search

from visualization import (
    plot_convergence,
    plot_final_comparison
)

# ---------------- NLP IMPORT ----------------
from nlp_constraints import parse_constraints


if __name__ == "__main__":

    # ---------------- LOAD DATA ----------------
    df = pd.read_csv("data/final_dataset.csv")

    # ---------------- ADMIN NLP INPUT ----------------
    admin_text = input(
        "Enter scheduling constraints:\n"
    )

    # ---------------- PARSE NLP ----------------
    parsed_constraints = parse_constraints(
        admin_text
    )

    print("\n=== PARSED CONSTRAINTS ===")
    print(parsed_constraints)

    # ---------------- GENERATE TIMETABLE ----------------
    timetable = generate_timetable(
        df,
        parsed_constraints
    )

    print("\n=== SAMPLE TIMETABLE ===")
    for t in timetable[:10]:
        print(t)

    print("\n=== INITIAL EVALUATION ===")
    print(evaluate_timetable(timetable))

    # ---------------- GA ----------------
    start = time.time()

    ga_best, ga_fit, ga_hist = run_genetic_algorithm(
        df,
        parsed_constraints
    )

    ga_time = time.time() - start

    print("GA Time:", ga_time)

    # ---------------- SA ----------------
    start = time.time()

    sa_best, sa_fit, sa_hist = run_simulated_annealing(
        df,
        parsed_constraints
    )

    sa_time = time.time() - start

    print("SA Time:", sa_time)

    # ---------------- TABU ----------------
    start = time.time()

    tabu_best, tabu_fit, tabu_hist = run_tabu_search(
        df,
        parsed_constraints
    )

    tabu_time = time.time() - start

    print("Tabu Time:", tabu_time)

    # ---------------- RESULTS ----------------
    print("\n=== FINAL RESULTS ===")

    print(f"Genetic Algorithm Best Fitness: {ga_fit}")
    print(f"Simulated Annealing Best Fitness: {sa_fit}")
    print(f"Tabu Search Best Fitness: {tabu_fit}")

    print(f"GA Time: {ga_time:.2f} sec")
    print(f"SA Time: {sa_time:.2f} sec")
    print(f"Tabu Time: {tabu_time:.2f} sec")

    best_score = min(
        ga_fit,
        sa_fit,
        tabu_fit
    )

    if best_score == ga_fit:
        best_algo = "Genetic Algorithm"

    elif best_score == sa_fit:
        best_algo = "Simulated Annealing"

    else:
        best_algo = "Tabu Search"

    print(f"\nBest Performing Algorithm: {best_algo}")
    print(f"Best Score: {best_score}")

    print("\n=== GA DETAILED EVALUATION ===")

    print(evaluate_timetable(ga_best))

    # ---------------- VISUALIZATION ----------------
    plot_convergence(
        ga_hist,
        sa_hist,
        tabu_hist
    )

    plot_final_comparison(
        ga_fit,
        sa_fit,
        tabu_fit
    )