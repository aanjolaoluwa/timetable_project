import pandas as pd
import matplotlib.pyplot as plt

from nlp_parser import save_constraints

# Updated Import block
from engine import (
    generate_timetable,
    evaluate_timetable,
    load_dataset,
    dataset_summary,
    print_dataset_venues
)

from algorithms.genetic_algorithm import (
    run_genetic_algorithm
)

from algorithms.simulated_annealing import (
    run_simulated_annealing
)

from algorithms.tabu_search import (
    run_tabu_search
)

# =====================================================
# NLP CONSTRAINT INPUT
# =====================================================

print("\n======================================")
print(" AI TIMETABLE SCHEDULING SYSTEM ")
print("======================================")

print("\nEnter Scheduling Constraints:")
print("Type constraints in English.")
print("Press ENTER twice when done.\n")



lines = []

while True:

    line = input()

    if line.strip() == "":
        break

    lines.append(line)

constraint_text = "\n".join(lines)

parsed_constraints = save_constraints(
    constraint_text
)

print("\n=== PARSED CONSTRAINTS ===\n")

for key, value in parsed_constraints.items():

    print(f"{key}: {value}")

# =====================================================
# LOAD CLEANED DATASET
# =====================================================

print("\nLoading cleaned dataset...\n")

df = load_dataset("data/cleaned_dataset.csv")
print("Dataset Loaded Successfully.")

print(f"Total Rows: {len(df)}")

# =====================================================
# CLEAN COLUMN NAMES
# =====================================================

df.columns = (
    df.columns
    .str.strip()
    .str.upper()
)

# =====================================================
# REQUIRED COLUMNS CHECK
# =====================================================

required_columns = [

    "COURSE CODE",
    "LECTURER",
    "STUDENTS",
    "CLASSROOM(VENUE)",
    "VENUE_CAPACITY"

]

missing_columns = [

    col for col in required_columns
    if col not in df.columns

]

if len(missing_columns) > 0:

    raise Exception(
        f"Missing columns: {missing_columns}"
    )

# =====================================================
# CLEAN STUDENTS COLUMN
# =====================================================

df["STUDENTS"] = pd.to_numeric(
    df["STUDENTS"],
    errors="coerce"
)

df["STUDENTS"] = (
    df["STUDENTS"]
    .fillna(0)
    .astype(int)
)

# =====================================================
# REMOVE INVALID ROWS
# =====================================================

df = df.dropna(
    subset=[
        "COURSE CODE",
        "LECTURER"
    ]
)

df = df[
    df["COURSE CODE"] != ""
]

print(
    f"\nRemaining Valid Rows: {len(df)}"
)

# =====================================================
# DATASET SUMMARY
# =====================================================

print("\n======================================")
print(" DATASET SUMMARY ")
print("======================================")

print(f"Total Courses: {len(df)}")

print(
    f"Unique Venues: "
    f"{df['CLASSROOM(VENUE)'].nunique()}"
)

print(
    f"Unique Lecturers: "
    f"{df['LECTURER'].nunique()}"
)

print(
    f"Maximum Students: "
    f"{df['STUDENTS'].max()}"
)

# =====================================================
# GENERATE INITIAL TIMETABLE
# =====================================================
df = load_dataset("data/cleaned_dataset.csv")

dataset_summary(df)

print_dataset_venues(df)

print("\nGenerating Initial Timetable...\n")

initial_timetable = generate_timetable(
    df,
    parsed_constraints
)

initial_evaluation = evaluate_timetable(
    initial_timetable,
    parsed_constraints
)

print("\n=== INITIAL EVALUATION ===\n")

print(initial_evaluation)

# =====================================================
# RUN GENETIC ALGORITHM
# =====================================================

print("\n======================================")
print(" RUNNING GENETIC ALGORITHM ")
print("======================================\n")

ga_solution, ga_fitness, ga_history = (
    run_genetic_algorithm(
        df,
        constraints=parsed_constraints,
        population_size=50,
        generations=100,
        mutation_rate=0.2
    )
)

print("\nGenetic Algorithm Completed.")

print(
    f"Best GA Fitness: {ga_fitness}"
)

# =====================================================
# RUN SIMULATED ANNEALING
# =====================================================

print("\n======================================")
print(" RUNNING SIMULATED ANNEALING ")
print("======================================\n")

sa_solution, sa_fitness, sa_history = (
    run_simulated_annealing(
        df,
        constraints=parsed_constraints,
        initial_solution=ga_solution,
        iterations=100
    )
)

print("\nSimulated Annealing Completed.")

print(
    f"Best SA Fitness: {sa_fitness}"
)

# =====================================================
# RUN TABU SEARCH
# =====================================================

print("\n======================================")
print(" RUNNING TABU SEARCH ")
print("======================================\n")

tabu_solution, tabu_fitness, tabu_history = (
    run_tabu_search(
        df,
        constraints=parsed_constraints,
        iterations=100
    )
)

print("\nTabu Search Completed.")

print(
    f"Best Tabu Fitness: {tabu_fitness}"
)

# =====================================================
# SELECT BEST SOLUTION
# =====================================================

best_solution = min(

    [

        (
            "Genetic Algorithm",
            ga_solution,
            ga_fitness
        ),

        (
            "Simulated Annealing",
            sa_solution,
            sa_fitness
        ),

        (
            "Tabu Search",
            tabu_solution,
            tabu_fitness
        )

    ],

    key=lambda x: x[2]

)

best_algorithm = best_solution[0]
best_timetable = best_solution[1]
best_fitness = best_solution[2]

# =====================================================
# FINAL RESULTS
# =====================================================

print("\n======================================")
print(" FINAL BEST SOLUTION ")
print("======================================\n")

print(
    f"Best Algorithm: "
    f"{best_algorithm}"
)

print(
    f"Best Fitness: "
    f"{best_fitness}"
)

# =====================================================
# SAVE FINAL TIMETABLE
# =====================================================

final_df = pd.DataFrame(
    best_timetable
)

final_df.to_csv(
    "final_timetable.csv",
    index=False
)

print(
    "\nFinal timetable saved as:"
)

print("final_timetable.csv")

# =====================================================
# DISPLAY SAMPLE OUTPUT
# =====================================================

print("\n=== SAMPLE TIMETABLE ===\n")

print(
    final_df.head(20)
)

# =====================================================
# VISUALIZE PERFORMANCE
# =====================================================

print("\nGenerating optimization graph...\n")

plt.figure(figsize=(12, 6))

plt.plot(
    ga_history,
    label="Genetic Algorithm"
)

plt.plot(
    sa_history,
    label="Simulated Annealing"
)

plt.plot(
    tabu_history,
    label="Tabu Search"
)

plt.xlabel("Iterations")

plt.ylabel("Fitness")

plt.title(
    "Optimization Performance"
)

plt.legend()

plt.grid(True)

plt.show()

# =====================================================
# FINAL MESSAGE
# =====================================================

print("\n======================================")
print(" TIMETABLE GENERATION COMPLETED ")
print("======================================")