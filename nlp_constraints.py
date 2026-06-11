import re


def parse_constraints(text):

    constraints = []

    text = text.lower()

    # ---------------- HARD CONSTRAINTS ----------------

    if "no lecturer" in text or "lecturer overlap" in text:
        constraints.append({
            "type": "hard",
            "constraint": "lecturer_no_overlap"
        })

    if "large classes" in text or "big halls" in text:
        match = re.search(r'above (\d+)', text)

        min_students = 150

        if match:
            min_students = int(match.group(1))

        constraints.append({
            "type": "hard",
            "constraint": "large_class_room",
            "min_students": min_students
        })

    # ---------------- SOFT CONSTRAINTS ----------------

    if "morning" in text:
        constraints.append({
            "type": "soft",
            "constraint": "morning_preference"
        })

    return constraints