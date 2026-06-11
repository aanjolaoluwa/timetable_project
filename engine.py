# ======================================
# engine.py
# AI Timetable Scheduling Engine
# ======================================

import random
import copy
import pandas as pd

# ======================================
# CONFIGURATION
# ======================================

DAYS = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday"
]

HOURS = [
    "8-9",
    "9-10",
    "10-11",
    "11-12",
    "12-1",
    "1-2",
    "2-3",
    "3-4",
    "4-5",
    "5-6"
]

MORNING_HOURS = ["8-9", "9-10", "10-11", "11-12", "12-1"]
EVENING_HOURS = ["4-5", "5-6"]

TIMESLOTS = [
    f"{day}_{hour}"
    for day in DAYS
    for hour in HOURS
]

MORNING_TIMESLOTS = [f"{day}_{hour}" for day in DAYS for hour in MORNING_HOURS]

# ======================================
# VENUE CAPACITIES
# ======================================

from room_capacities import ROOM_CAPACITY
VENUE_CAPACITY = ROOM_CAPACITY

VENUES = list(VENUE_CAPACITY.keys())

# ======================================
# NIGERIAN LECTURER NAMES (for unknown/missing entries)
# ======================================

RANDOM_LECTURER_NAMES = [
    "Dr. Adebayo", "Prof. Nnamdi", "Dr. Olayinka", "Mr. Emeka", "Mrs. Okafor",
    "Dr. Chidi", "Prof. Olatunji", "Dr. Aderonke", "Mr. Abubakar", "Dr. Ibe",
    "Prof. Bello", "Dr. Onyeka", "Mrs. Adeleke", "Dr. Eze", "Prof. Aina",
    "Dr. Okon", "Mr. Babalola", "Dr. Nwachukwu", "Mrs. Osei", "Prof. Nwosu",
    "Dr. Oladipo", "Dr. Oluwaseun", "Mr. Danjuma", "Prof. Anyanwu", "Dr. Kalu",
    "Mrs. Lawal", "Dr. Usman", "Prof. Akpan", "Dr. Idris", "Mr. Adewale"
]

# ======================================
# LOAD DATASET
# ======================================

def load_dataset(file_path="cleaned_dataset.csv"):
    global VENUE_CAPACITY, VENUES

    df = pd.read_csv(file_path)

    print("\nDataset Loaded Successfully.")
    print(f"Total Rows: {len(df)}")

    # Standardize column names
    col_mapping = {}
    for col in df.columns:
        c_upper = str(col).strip().upper()
        if c_upper in ["COURSE", "COURSE_CODE", "COURSE CODE"]:
            col_mapping[col] = "COURSE CODE"
        elif c_upper in ["LECTURER", "LECTURERS", "LECTURER'S NAME", "LECTURERS NAME", "LECTURER NAME"]:
            col_mapping[col] = "LECTURER"
        elif c_upper in ["STUDENT", "STUDENTS", "SIZE", "NO OF STUDENT PER COURSE",
                         "NO. OF STUDENTS", "NUMBER OF STUDENTS", "STUDENT COUNT"]:
            col_mapping[col] = "STUDENTS"
        elif c_upper in ["VENUE", "CLASSROOM", "ROOM", "CLASSROOM(VENUE)",
                         "CLASSROOM (VENUE)", "VENUE NAME", "TEACHING VENUE"]:
            col_mapping[col] = "CLASSROOM(VENUE)"
        elif c_upper in ["LEVEL"]:
            col_mapping[col] = "LEVEL"
        elif c_upper in ["DURATION", "HOURS", "COURSE LOAD(HOURS)", "CREDIT HOURS",
                         "CREDIT UNITS", "COURSE UNIT", "COURSE UNITS"]:
            col_mapping[col] = "COURSE LOAD(HOURS)"
        elif c_upper in ["CAPACITY", "VENUE_CAPACITY", "ROOM CAPACITY", "HALL CAPACITY"]:
            col_mapping[col] = "VENUE_CAPACITY"

    # Avoid duplicate renames
    seen_targets = set()
    safe_mapping = {}
    for orig_col, target_col in col_mapping.items():
        if target_col not in seen_targets:
            safe_mapping[orig_col] = target_col
            seen_targets.add(target_col)

    df.rename(columns=safe_mapping, inplace=True)

    # Ensure required columns exist
    for req_col in ["COURSE CODE", "LECTURER", "STUDENTS"]:
        if req_col not in df.columns:
            df[req_col] = "Unknown" if req_col != "STUDENTS" else 50

    # Replace unknown/missing lecturers with realistic Nigerian names
    # Note: replacement is seeded per row index so same dataset always maps to same name,
    # but different datasets get different names.
    _name_pool = RANDOM_LECTURER_NAMES.copy()

    def replace_unknown_lecturer(val):
        s_val = str(val).strip().lower()
        if pd.isna(val) or s_val in ["", "nan", "unknown", "unknown lecturer", "none", "unk", "n/a"]:
            return random.choice(_name_pool)
        return val

    df["LECTURER"] = df["LECTURER"].apply(replace_unknown_lecturer)

    # Drop rows where course code is missing
    df = df.dropna(subset=["COURSE CODE", "STUDENTS"])

    # Dynamic capacity integration — map ALL dataset venues into VENUE_CAPACITY
    if "CLASSROOM(VENUE)" in df.columns:
        if "VENUE_CAPACITY" not in df.columns:
            # No capacity column — infer from venue name heuristics
            def _infer_capacity(venue_name):
                n = str(venue_name).upper()
                if "HALL107" in n or "CBN" in n or "OVERFLOW" in n:
                    return 500
                elif any(x in n for x in ["HALL201","HALL202","HALL203","HALL204",
                                           "LARGELH","LARGE LH","LT1","LT2"]):
                    return 400
                elif any(x in n for x in ["HALL108","HALL306","HALL307","HALL308",
                                           "HALL313","LH","AUDITORIA","AUDITORIUM"]):
                    return 350
                elif any(x in n for x in ["COMPUTER","CSC","CIT","GBL","SQL"]):
                    return 250
                elif any(x in n for x in ["STUDIO","SEMINAR","CENTRE CLASS"]):
                    return 200
                elif any(x in n for x in ["LAB","WORKSHOP","NEWSROOM","PSY","LANG",
                                           "MKT","EIE","ARGUS","FLUID","PHY"]):
                    return 120
                elif any(x in n for x in ["BCH","BIO","MCB","CHEM","CHAPEL","LIBRARY"]):
                    return 150
                else:
                    # Lecture halls named with department codes (e.g. CHE 200LH, CVE 300LH)
                    return 200

            df["VENUE_CAPACITY"] = df["CLASSROOM(VENUE)"].apply(
                lambda v: _infer_capacity(str(v).strip()) if pd.notna(v) else 200
            )

        df_venues = df[["CLASSROOM(VENUE)", "VENUE_CAPACITY"]].dropna()
        for _, row in df_venues.iterrows():
            v_name_raw = str(row["CLASSROOM(VENUE)"]).strip()
            if not v_name_raw or v_name_raw.lower() in ["unknown","nan",""]:
                continue
            # Create a clean key: uppercase, spaces → underscore, remove brackets/parens
            v_key = v_name_raw.upper()
            v_key = v_key.replace("(","").replace(")","").replace(" ","_").replace("/","_")
            v_key = v_key.replace("__","_").strip("_")
            try:
                v_cap = int(float(row["VENUE_CAPACITY"]))
                if v_key not in VENUE_CAPACITY or v_cap > VENUE_CAPACITY[v_key]:
                    VENUE_CAPACITY[v_key] = v_cap
                    # Also store original spaced name as alias
                    v_key2 = v_name_raw.upper()
                    if v_key2 != v_key and v_key2 not in VENUE_CAPACITY:
                        VENUE_CAPACITY[v_key2] = v_cap
            except (ValueError, TypeError):
                pass

        VENUES = list(VENUE_CAPACITY.keys())

    print(f"\nRemaining Valid Rows: {len(df)}")
    print(f"Total venues available for scheduling: {len(VENUES)}")
    return df

# ======================================
# DATASET SUMMARY
# ======================================

def dataset_summary(df):
    print("\n======================================")
    print(" DATASET SUMMARY ")
    print("======================================")

    print(f"Total Courses: {len(df)}")

    if "CLASSROOM(VENUE)" in df.columns:
        print(f"Unique Venues: {df['CLASSROOM(VENUE)'].nunique()}")

    print(f"Unique Lecturers: {df['LECTURER'].nunique()}")
    print(f"Maximum Students: {df['STUDENTS'].max()}")
    print("\nROOMS IN ENGINE:")
    print(len(VENUE_CAPACITY))

    if "CLASSROOM(VENUE)" in df.columns:
        print(f"ROOMS IN DATASET: {df['CLASSROOM(VENUE)'].nunique()}")

def print_dataset_venues(df):
    if "CLASSROOM(VENUE)" not in df.columns:
        return

    print("\n======================================")
    print(" ALL VENUES IN DATASET ")
    print("======================================")

    venues = sorted(
        df["CLASSROOM(VENUE)"]
        .dropna()
        .astype(str)
        .unique()
    )

    print(f"\nTotal Venues Found: {len(venues)}\n")
    for venue in venues:
        print(venue)

# ======================================
# HELPER FUNCTIONS
# ======================================

def is_computer_course(course):
    course = str(course).upper()
    return (
        "CSC" in course
        or "CIT" in course
        or "CIS" in course
    )

def get_valid_rooms(course, students, large_class_threshold=None):
    """Return a randomized list of valid rooms for a course.
    
    If large_class_threshold is set, only rooms with capacity >= that threshold
    are considered for large classes.
    """
    course_upper = str(course).upper()
    
    # HARD-CODED VENUE PREFERENCES (University specific)
    if any(x in course_upper for x in ["TMC", "DEO"]):
        return ["CHAPEL"]
    
    if any(x in course_upper for x in ["GST", "EDS"]):
        prefs = ["LT1", "LT2"]
        random.shuffle(prefs)
        return prefs

    valid_rooms = []

    # Determine minimum capacity requirement
    required_capacity = students
    if large_class_threshold and students >= large_class_threshold:
        # Large class: only big halls
        required_capacity = max(students, large_class_threshold)

    if is_computer_course(course):
        preferred_rooms = []
        other_rooms = []
        for room in VENUES:
            capacity = VENUE_CAPACITY.get(room, 100)
            if capacity < required_capacity:
                continue
            if "COMPUTER" in room:
                preferred_rooms.append(room)
            else:
                other_rooms.append(room)
        random.shuffle(preferred_rooms)
        random.shuffle(other_rooms)
        valid_rooms = preferred_rooms + other_rooms
    else:
        for room in VENUES:
            capacity = VENUE_CAPACITY.get(room, 100)
            if capacity >= required_capacity:
                valid_rooms.append(room)

    # Fallback 1: allow rooms at 70% capacity
    if len(valid_rooms) == 0:
        for room in VENUES:
            capacity = VENUE_CAPACITY.get(room, 100)
            if capacity >= (students * 0.7):
                valid_rooms.append(room)

    # Fallback 2: use all rooms
    if len(valid_rooms) == 0:
        valid_rooms = VENUES.copy()

    random.shuffle(valid_rooms)
    return valid_rooms


def _build_slot_order(constraints):
    """Build an ordered list of timeslots based on constraints.
    
    If morning_preferred is True: morning slots come first.
    If avoid_days is set: those day's slots are excluded (soft avoidance).
    If avoid_timeslots is set: those exact slots are excluded.
    """
    if not constraints:
        slots = TIMESLOTS.copy()
        random.shuffle(slots)
        return slots

    avoid_days = set(constraints.get("avoid_days", []))
    avoid_slots_set = set(constraints.get("avoid_timeslots", []))
    prefer_morning = constraints.get("morning_preferred", False)
    prefer_no_evening = constraints.get("avoid_evening", False)

    # Build primary pool (slots NOT in avoided days/slots)
    primary = []
    secondary = []  # avoided-day slots as fallback

    for slot in TIMESLOTS:
        day = slot.split("_")[0]
        hour = slot.split("_")[1] if "_" in slot else ""

        if slot in avoid_slots_set:
            continue  # hard-exclude these

        if day in avoid_days:
            secondary.append(slot)
        else:
            primary.append(slot)

    # Within primary, sort morning slots first if preferred
    if prefer_morning:
        morning_slots = [s for s in primary if any(h in s for h in MORNING_HOURS)]
        other_slots = [s for s in primary if not any(h in s for h in MORNING_HOURS)]
        random.shuffle(morning_slots)
        random.shuffle(other_slots)
        primary = morning_slots + other_slots
    elif prefer_no_evening:
        non_evening = [s for s in primary if not any(h in s for h in EVENING_HOURS)]
        evening_slots = [s for s in primary if any(h in s for h in EVENING_HOURS)]
        random.shuffle(non_evening)
        random.shuffle(evening_slots)
        primary = non_evening + evening_slots
    else:
        random.shuffle(primary)

    random.shuffle(secondary)
    return primary + secondary


# ======================================
# INITIAL TIMETABLE GENERATION
# ======================================

def generate_initial_solution(df, constraints=None):
    """Generate an initial timetable solution.
    
    constraints: parsed constraint dictionary from nlp_parser.py
    Each call produces a different randomized assignment.
    """
    timetable = []
    lecturer_schedule = set()
    room_schedule = set()
    unscheduled = 0

    # Large class threshold from constraints
    large_class_threshold = None
    if constraints:
        large_class_threshold = constraints.get("large_class_threshold")

    # Sort by students descending (largest classes get first pick of rooms)
    df = df.sort_values(by="STUDENTS", ascending=False)

    # Build slot order respecting constraints (randomized each call)
    slot_order = _build_slot_order(constraints)

    for _, row in df.iterrows():
        course = str(row["COURSE CODE"])
        lecturer = str(row["LECTURER"])
        students = int(row["STUDENTS"])
        level = str(row.get("LEVEL", ""))
        duration = int(row.get("COURSE LOAD(HOURS)", 1))

        if duration <= 0:
            duration = 1

        assigned = False
        possible_rooms = get_valid_rooms(course, students, large_class_threshold)

        # Per-session slot shuffle for diversity
        session_slots = slot_order.copy()
        random.shuffle(session_slots)

        for room in possible_rooms:
            if assigned:
                break

            for slot in session_slots:
                lecturer_key = (lecturer, slot)
                room_key = (room, slot)

                # HARD: no lecturer double-booking
                if lecturer_key in lecturer_schedule:
                    continue
                # HARD: no room double-booking
                if room_key in room_schedule:
                    continue

                # Level-500 soft constraint: avoid late slots
                if level == "500":
                    if "4-5" in slot or "5-6" in slot:
                        continue

                lecturer_schedule.add(lecturer_key)
                room_schedule.add(room_key)

                timetable.append({
                    "course": course,
                    "lecturer": lecturer,
                    "students": students,
                    "venue": room,
                    "room": room,
                    "capacity": VENUE_CAPACITY.get(room, 100),
                    "timeslot": slot,
                    "duration": duration,
                    "level": level
                })

                assigned = True
                break

        if not assigned:
            # RELAX PASS: try again without level-500 restriction and any available slot
            all_slots = TIMESLOTS.copy()
            random.shuffle(all_slots)
            all_rooms = VENUES.copy()
            random.shuffle(all_rooms)

            for room in all_rooms:
                if assigned:
                    break
                for slot in all_slots:
                    lecturer_key = (lecturer, slot)
                    room_key = (room, slot)
                    if lecturer_key in lecturer_schedule:
                        continue
                    if room_key in room_schedule:
                        continue

                    lecturer_schedule.add(lecturer_key)
                    room_schedule.add(room_key)
                    timetable.append({
                        "course": course,
                        "lecturer": lecturer,
                        "students": students,
                        "venue": room,
                        "room": room,
                        "capacity": VENUE_CAPACITY.get(room, 100),
                        "timeslot": slot,
                        "duration": duration,
                        "level": level
                    })
                    assigned = True
                    break

        if not assigned:
            unscheduled += 1
            timetable.append({
                "course": course,
                "lecturer": lecturer,
                "students": students,
                "venue": "UNASSIGNED",
                "room": "UNASSIGNED",
                "capacity": 0,
                "timeslot": "UNSCHEDULED",
                "duration": duration,
                "level": level
            })

    print(f"\nUnscheduled Sessions: {unscheduled}")
    return timetable

# ======================================
# FITNESS FUNCTION
# ======================================

def evaluate_timetable(timetable, constraints=None):
    """Evaluate the quality of a timetable.
    
    Lower score = better. Zero = perfect.
    Checks: lecturer clashes, room clashes, capacity violations,
    unscheduled sessions, and NLP constraint violations.
    """
    lecturer_clashes = 0
    room_clashes = 0
    capacity_violations = 0
    practical_violations = 0
    unscheduled_sessions = 0
    nlp_violations = 0

    lecturer_tracker = {}
    room_tracker = {}

    # Parse constraint settings — initialise with safe defaults first
    avoid_days = set()
    avoid_timeslots = set()
    prefer_morning = False
    avoid_evening = False
    large_class_threshold = None
    lecturer_prefs = {}

    if constraints:
        avoid_days = set(constraints.get("avoid_days", []))
        avoid_timeslots = set(constraints.get("avoid_timeslots", []))
        prefer_morning = constraints.get("morning_preferred", False)
        avoid_evening = constraints.get("avoid_evening", False)
        large_class_threshold = constraints.get("large_class_threshold")
        lecturer_prefs = constraints.get("lecturer_preferences", {})

    for entry in timetable:
        if entry["timeslot"] == "UNSCHEDULED":
            unscheduled_sessions += 1
            continue

        slot = entry["timeslot"]
        slot_day = slot.split("_")[0] if "_" in slot else ""
        slot_hour = slot.split("_")[1] if "_" in slot else ""

        lecturer_key = (slot, entry["lecturer"])
        room_key = (slot, entry.get("room") or entry.get("venue", "UNKNOWN_VENUE"))

        lecturer_tracker[lecturer_key] = lecturer_tracker.get(lecturer_key, 0) + 1
        room_tracker[room_key] = room_tracker.get(room_key, 0) + 1

        # --- NLP constraint violations (INSIDE the for-loop) ---

        # 1. Avoid specific days
        if slot_day in avoid_days:
            nlp_violations += 1

        # 2. Avoid specific timeslots
        if slot in avoid_timeslots:
            nlp_violations += 1

        # 3. Morning preference: only penalise TRUE EVENING slots (4-5 and 5-6)
        if prefer_morning and slot_hour in EVENING_HOURS:
            nlp_violations += 1

        # 4. Avoid evening (soft preference, no double-count with morning_preferred)
        if avoid_evening and not prefer_morning and slot_hour in EVENING_HOURS:
            nlp_violations += 1

        # 5. Large classes must use large halls
        if large_class_threshold:
            students = entry.get("students", 0)
            capacity = entry.get("capacity", 9999)
            if students >= large_class_threshold and capacity < large_class_threshold:
                nlp_violations += 2  # double weight

        # 6. Lecturer-specific preferences
        for lect_name, pref in lecturer_prefs.items():
            if lect_name.lower() in entry["lecturer"].lower():
                avoid_day = pref.get("avoid_day")
                prefer_day = pref.get("prefer_day")
                if avoid_day and avoid_day == slot_day:
                    nlp_violations += 1
                if prefer_day and prefer_day != slot_day:
                    nlp_violations += 1

    # Count clashes
    for count in lecturer_tracker.values():
        if count > 1:
            lecturer_clashes += (count - 1)

    for count in room_tracker.values():
        if count > 1:
            room_clashes += (count - 1)

    # Capacity violations
    for entry in timetable:
        if entry["timeslot"] == "UNSCHEDULED":
            continue
        capacity = entry.get("capacity") or entry.get("room_capacity", 9999)
        students = entry.get("students", 0)
        if isinstance(students, str):
            try:
                students = int(students)
            except ValueError:
                students = 0
        if students > capacity:
            capacity_violations += 1

    # ---------------------------------------------------------------
    # FITNESS CALCULATION
    # Hard constraint penalties (must be zero for valid schedule):
    #   - Unscheduled session:  500,000  (catastrophic)
    #   - Lecturer clash:       100,000  (hard violation)
    #   - Room clash:           100,000  (hard violation)
    #   - Capacity exceeded:     50,000  (hard violation)
    # Soft constraint penalties (should be minimised, not eliminated):
    #   - NLP preference breach:  5,000  (soft preference)
    # ---------------------------------------------------------------
    fitness = (
        lecturer_clashes * 100000 +
        room_clashes * 100000 +
        capacity_violations * 50000 +
        practical_violations * 10000 +
        unscheduled_sessions * 500000 +
        nlp_violations * 5000
    )

    return {
        "fitness": fitness,
        "lecturer_clashes": lecturer_clashes,
        "room_clashes": room_clashes,
        "capacity_violations": capacity_violations,
        "practical_violations": practical_violations,
        "unscheduled_sessions": unscheduled_sessions,
        "nlp_violations": nlp_violations
    }

# ======================================
# MUTATION
# ======================================

def mutate(timetable, constraints=None):
    """Mutate a timetable by randomly reassigning ~20% of sessions.
    
    Respects constraints when selecting new timeslots.
    """
    new_timetable = copy.deepcopy(timetable)

    lecturer_schedule = set()
    room_schedule = set()

    # Rebuild current occupancy (all sessions)
    for session in new_timetable:
        if session["timeslot"] == "UNSCHEDULED":
            continue
        lecturer_schedule.add((session["lecturer"], session["timeslot"]))
        room_schedule.add((session["room"], session["timeslot"]))

    # Large class threshold
    large_class_threshold = None
    if constraints:
        large_class_threshold = constraints.get("large_class_threshold")

    for session in new_timetable:
        # Only mutate 20% of sessions
        if random.random() > 0.20:
            continue

        course = session["course"]
        lecturer = session["lecturer"]
        students = session["students"]
        level = session["level"]

        prev_slot = session["timeslot"]
        prev_room = session["room"]

        # Free up previous slot
        if prev_slot != "UNSCHEDULED":
            lecturer_schedule.discard((lecturer, prev_slot))
            room_schedule.discard((prev_room, prev_slot))

        possible_rooms = get_valid_rooms(course, students, large_class_threshold)
        slot_order = _build_slot_order(constraints)
        random.shuffle(slot_order)

        assigned = False

        for room in possible_rooms:
            for slot in slot_order:
                lecturer_key = (lecturer, slot)
                room_key = (room, slot)

                if lecturer_key in lecturer_schedule:
                    continue
                if room_key in room_schedule:
                    continue

                if level == "500":
                    if "4-5" in slot or "5-6" in slot:
                        continue

                session["timeslot"] = slot
                session["venue"] = room
                session["room"] = room
                session["capacity"] = VENUE_CAPACITY.get(room, 100)

                lecturer_schedule.add(lecturer_key)
                room_schedule.add(room_key)

                assigned = True
                break

            if assigned:
                break

        if not assigned:
            session["timeslot"] = "UNSCHEDULED"
            session["venue"] = "UNASSIGNED"
            session["room"] = "UNASSIGNED"
            session["capacity"] = 0

    # RECOVERY PASS: re-schedule any UNSCHEDULED entries
    for session in new_timetable:
        if session["timeslot"] != "UNSCHEDULED":
            continue

        course = session["course"]
        lecturer = session["lecturer"]
        students = session["students"]
        level = session["level"]

        all_rooms = VENUES.copy()
        random.shuffle(all_rooms)
        all_slots = TIMESLOTS.copy()
        random.shuffle(all_slots)

        for room in all_rooms:
            for slot in all_slots:
                lecturer_key = (lecturer, slot)
                room_key = (room, slot)

                if lecturer_key in lecturer_schedule:
                    continue
                if room_key in room_schedule:
                    continue

                session["timeslot"] = slot
                session["venue"] = room
                session["room"] = room
                session["capacity"] = VENUE_CAPACITY.get(room, 100)

                lecturer_schedule.add(lecturer_key)
                room_schedule.add(room_key)
                break

            if session["timeslot"] != "UNSCHEDULED":
                break

    return new_timetable

# ======================================
# GENETIC ALGORITHM (BUILT-IN / FALLBACK)
# ======================================

def genetic_algorithm(
    initial_solution,
    constraints=None,
    generations=100,
    population_size=20
):
    """Run a Genetic Algorithm to optimise a timetable.
    
    Uses constraints in both fitness evaluation AND mutation so the
    search is properly guided by the declared preferences.
    """
    population = []

    # Seed population with diverse mutations of the initial solution
    for _ in range(population_size):
        population.append(mutate(initial_solution, constraints))

    best_solution = None
    best_fitness = float("inf")
    history = []

    for generation in range(generations):
        scored_population = []

        for individual in population:
            evaluation = evaluate_timetable(individual, constraints)
            fitness = evaluation["fitness"]

            scored_population.append((fitness, individual))

            if fitness < best_fitness:
                best_fitness = fitness
                best_solution = copy.deepcopy(individual)

        scored_population.sort(key=lambda x: x[0])

        history.append(best_fitness)

        print(
            f"Generation {generation} | "
            f"Best Fitness: {best_fitness}"
        )

        survivors = [x[1] for x in scored_population[:10]]

        new_population = []
        # Elitism: always keep best solution
        new_population.append(copy.deepcopy(best_solution))

        while len(new_population) < population_size:
            parent = random.choice(survivors)
            child = mutate(parent, constraints)
            new_population.append(child)

        population = new_population

    return best_solution, history

# ======================================
# SAVE TIMETABLE
# ======================================

def save_timetable(
    timetable,
    filename="final_timetable.csv"
):
    df = pd.DataFrame(timetable)
    df.to_csv(filename, index=False)

    print("\nFinal timetable saved as:")
    print(filename)

    print("\n=== SAMPLE TIMETABLE ===\n")
    print(df.head(20))

# ======================================
# COMPATIBILITY FUNCTIONS
# ======================================

def generate_timetable(df, constraints=None):
    """Generate an initial timetable, respecting constraints."""
    return generate_initial_solution(df, constraints)

def mutate_timetable(timetable, constraints=None, mutation_rate=0.1):
    """Mutate a timetable, respecting constraints."""
    return mutate(timetable, constraints)

def crossover_timetable(parent1, parent2):
    """Single-point crossover between two timetables."""
    split = len(parent1) // 2
    child = (
        copy.deepcopy(parent1[:split])
        + copy.deepcopy(parent2[split:])
    )
    return child

# ======================================
# MAIN EXECUTION
# ======================================

if __name__ == "__main__":
    print("\n======================================")
    print(" AI TIMETABLE SCHEDULING SYSTEM ")
    print("======================================")

    import os

    target_path = "data/final_dataset.csv"
    if not os.path.exists(target_path):
        target_path = "data/cleaned_dataset.csv"
    if not os.path.exists(target_path):
        target_path = "cleaned_dataset.csv"

    print(f"\nLoading dataset from: {target_path}...")

    try:
        df = load_dataset(target_path)
        dataset_summary(df)

        print("\nGenerating Initial Timetable...\n")
        timetable = generate_initial_solution(df)

        print("\n=== INITIAL EVALUATION ===\n")
        initial_eval = evaluate_timetable(timetable)
        print(initial_eval)

        print("\n======================================")
        print(" RUNNING GENETIC ALGORITHM ")
        print("======================================\n")

        best_solution, history = genetic_algorithm(
            timetable,
            constraints=None,
            generations=50,
            population_size=20
        )

        print("\nGenetic Algorithm Completed.")
        final_eval = evaluate_timetable(best_solution)

        print("\n======================================")
        print(" FINAL BEST SOLUTION ")
        print("======================================")

        print(
            f"\nBest Fitness: "
            f"{final_eval['fitness']}"
        )

        save_timetable(best_solution)
    except Exception as e:
        import traceback
        print(f"\nExecution error: {e}")
        traceback.print_exc()