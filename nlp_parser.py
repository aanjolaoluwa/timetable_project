import re
import json


# =====================================================
# NLP CONSTRAINT PARSER
# Parses plain-English scheduling rules into a
# structured dictionary that engine.py can use directly.
#
# Supported constraint keys (output dictionary):
#   avoid_days          : list[str]  e.g. ["Saturday", "Friday"]
#   avoid_timeslots     : list[str]  e.g. ["Friday_4-5", "Friday_5-6"]
#   morning_preferred   : bool
#   avoid_evening       : bool
#   large_class_threshold : int|None  (e.g. 150 — classes above this use big halls)
#   lecturer_no_overlap : bool        (always True, enforced as hard constraint)
#   lecturer_preferences: dict        {name_fragment: {"avoid_day": "Monday"}}
# =====================================================

DAYS_MAP = {
    "monday": "Monday",
    "tuesday": "Tuesday",
    "wednesday": "Wednesday",
    "thursday": "Thursday",
    "friday": "Friday",
    "saturday": "Saturday",
    "sunday": "Sunday",
    # short forms
    "mon": "Monday",
    "tue": "Tuesday",
    "wed": "Wednesday",
    "thu": "Thursday",
    "fri": "Friday",
    "sat": "Saturday",
    "sun": "Sunday",
}

HOURS_LIST = ["8-9", "9-10", "10-11", "11-12", "12-1", "1-2", "2-3", "3-4", "4-5", "5-6"]
MORNING_HOURS = {"8-9", "9-10", "10-11", "11-12", "12-1"}
EVENING_HOURS = {"4-5", "5-6"}
AFTERNOON_HOURS = {"2-3", "3-4", "4-5", "5-6"}

ALL_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]


def _extract_avoid_days(text):
    """Extract days that should be avoided from the constraint text."""
    avoid = set()

    # Patterns: "no classes on Friday", "avoid Saturday", "not on Monday", "no Monday classes"
    patterns = [
        r"no\s+(?:classes?|lectures?|sessions?|courses?)\s+on\s+(\w+)",
        r"avoid\s+(?:scheduling\s+(?:on|for)\s+)?(\w+)",
        r"not\s+on\s+(\w+)",
        r"(\w+)\s+(?:is|are|should be)\s+(?:free|off|excluded|avoided)",
        r"no\s+(\w+)\s+(?:classes?|lectures?|sessions?|courses?)",
        r"exclude\s+(\w+)",
        r"skip\s+(\w+)",
    ]

    for pattern in patterns:
        for match in re.finditer(pattern, text):
            word = match.group(1).lower().strip()
            if word in DAYS_MAP:
                avoid.add(DAYS_MAP[word])

    # "Weekends" → Saturday + Sunday
    if re.search(r"weekend", text):
        avoid.update(["Saturday", "Sunday"])

    return sorted(avoid)


def _extract_avoid_timeslots(text, avoid_days):
    """Extract specific timeslots to avoid (e.g. late Friday, after 4pm)."""
    avoid_slots = set()

    # All slots for avoided days are already handled via avoid_days
    # Here we handle cross-day time avoidances

    # "no classes after 4pm" / "avoid after 4" / "no evening classes" / "no late slots"
    evening_patterns = [
        r"after\s+(?:4|4pm|4\s*pm|16:00)",
        r"avoid\s+(?:the\s+)?evening",
        r"no\s+evening",
        r"no\s+late\s+(?:classes?|lectures?|slots?)",
        r"avoid\s+late",
        r"evening\s+(?:classes?|lectures?|slots?)\s+(?:are\s+)?(?:not\s+)?(?:preferred|allowed|desired|wanted)",
    ]
    avoid_evening = any(re.search(p, text) for p in evening_patterns)

    # "no classes after 5pm" / "avoid after 5"
    after5_patterns = [
        r"after\s+(?:5|5pm|5\s*pm|17:00)",
        r"no\s+5[-–]6\s+(?:classes?|lectures?)?",
    ]
    avoid_after5 = any(re.search(p, text) for p in after5_patterns)

    # "late Friday" / "avoid Friday afternoon"
    late_friday_patterns = [
        r"(?:late|afternoon|evening)\s+(?:on\s+)?friday",
        r"friday\s+(?:afternoon|evening|late)",
        r"no\s+friday\s+(?:afternoon|evening|late)",
    ]
    avoid_late_friday = any(re.search(p, text) for p in late_friday_patterns)

    for day in ALL_DAYS:
        for hour in HOURS_LIST:
            slot = f"{day}_{hour}"
            if avoid_evening and hour in EVENING_HOURS:
                avoid_slots.add(slot)
            if avoid_after5 and hour == "5-6":
                avoid_slots.add(slot)
            if avoid_late_friday and day == "Friday" and hour in AFTERNOON_HOURS:
                avoid_slots.add(slot)

    return sorted(avoid_slots)


def _extract_morning_preference(text):
    """Check if morning classes are preferred."""
    morning_patterns = [
        r"morning\s+(?:classes?|lectures?|slots?|preference|preferred|sessions?)",
        r"prefer\s+(?:the\s+)?morning",
        r"early\s+(?:classes?|lectures?|slots?|sessions?)",
        r"classes?\s+(?:in\s+)?(?:the\s+)?morning",
        r"morning\s+(?:is|are)\s+(?:preferred|better|ideal|best)",
        r"schedule\s+(?:in|for|during)\s+(?:the\s+)?morning",
    ]
    return any(re.search(p, text) for p in morning_patterns)


def _extract_avoid_evening(text):
    """Check if evening slots should be avoided (softer than specific avoidance)."""
    patterns = [
        r"avoid\s+evening",
        r"no\s+evening",
        r"avoid\s+late",
        r"evening\s+(?:classes?|lectures?)\s+(?:not\s+)?preferred",
    ]
    return any(re.search(p, text) for p in patterns)


def _extract_large_class_threshold(text):
    """Extract minimum student count for large class / big hall constraint."""
    # "large classes above 150", "classes with more than 200 students in big halls"
    patterns = [
        r"(?:large\s+classes?|classes?)\s+(?:above|over|more\s+than|with\s+more\s+than)\s+(\d+)",
        r"above\s+(\d+)\s+(?:students?\s+)?(?:use|in|need|require)(?:s)?\s+(?:big|large)\s+(?:halls?|rooms?|venues?)",
        r"big\s+halls?\s+for\s+(?:classes?|courses?)\s+(?:above|over|more\s+than)\s+(\d+)",
        r"(\d+)\s+(?:or\s+more\s+)?students?\s+(?:must\s+)?(?:use|get)\s+(?:big|large)\s+(?:halls?|rooms?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    # If they say "large classes big halls" without a number, default to 150
    default_patterns = [
        r"large\s+classes?\s+(?:in|use|should\s+use|must\s+use)\s+(?:big|large)\s+(?:halls?|rooms?)",
        r"big\s+halls?\s+for\s+large\s+classes?",
        r"high\s+capacity\s+(?:rooms?|halls?|venues?)",
    ]
    if any(re.search(p, text) for p in default_patterns):
        return 150

    return None


def _extract_lecturer_preferences(text):
    """Extract per-lecturer day preferences.
    
    E.g. "Dr. Adebayo should not teach on Mondays"
        "Prof. Bello prefers Tuesdays"
    """
    prefs = {}

    # Pattern: name + "should not / avoid / no" + day
    avoid_day_patterns = [
        r"((?:dr|prof|mr|mrs|ms)\.?\s+\w+)\s+(?:should\s+not|must\s+not|cannot|can't|doesn't?|avoid(?:s?)|prefers?\s+not)\s+(?:teach|lecture|be scheduled|have classes?)\s+on\s+(\w+)",
        r"((?:dr|prof|mr|mrs|ms)\.?\s+\w+)\s+is\s+not\s+available\s+on\s+(\w+)",
        r"exclude\s+((?:dr|prof|mr|mrs|ms)\.?\s+\w+)\s+(?:from\s+)?(\w+)",
        r"((?:dr|prof|mr|mrs|ms)\.?\s+\w+)\s+(?:has\s+)?no\s+(\w+)\s+(?:classes?|lectures?)",
    ]

    prefer_day_patterns = [
        r"((?:dr|prof|mr|mrs|ms)\.?\s+\w+)\s+prefers?\s+(\w+)",
        r"((?:dr|prof|mr|mrs|ms)\.?\s+\w+)\s+(?:teaches?|lectures?)\s+(?:only\s+)?on\s+(\w+)",
    ]

    for pattern in avoid_day_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1).strip().title()
            day_word = match.group(2).lower().strip().rstrip("s")  # "mondays" → "monday"
            if day_word in DAYS_MAP:
                prefs.setdefault(name, {})["avoid_day"] = DAYS_MAP[day_word]

    for pattern in prefer_day_patterns:
        for match in re.finditer(pattern, text, re.IGNORECASE):
            name = match.group(1).strip().title()
            day_word = match.group(2).lower().strip().rstrip("s")
            if day_word in DAYS_MAP:
                prefs.setdefault(name, {})["prefer_day"] = DAYS_MAP[day_word]

    return prefs


# =====================================================
# MAIN PARSE FUNCTION
# =====================================================

def parse_constraints(text):
    """Parse natural-language constraint text into a structured constraint dict.
    
    The returned dictionary is directly consumed by engine.evaluate_timetable()
    and engine.generate_initial_solution() / engine.mutate().
    
    Returns:
        dict with keys:
            avoid_days, avoid_timeslots, morning_preferred, avoid_evening,
            large_class_threshold, lecturer_no_overlap, lecturer_preferences
    """
    text = text.strip().lower()

    avoid_days = _extract_avoid_days(text)
    avoid_timeslots = _extract_avoid_timeslots(text, avoid_days)
    morning_preferred = _extract_morning_preference(text)
    avoid_evening = _extract_avoid_evening(text) or bool(avoid_timeslots)
    large_class_threshold = _extract_large_class_threshold(text)
    lecturer_prefs = _extract_lecturer_preferences(text)

    # Lecturer no-overlap is always True (enforced as hard constraint in engine)
    lecturer_no_overlap = True

    constraints = {
        "avoid_days": avoid_days,
        "avoid_timeslots": avoid_timeslots,
        "morning_preferred": morning_preferred,
        "avoid_evening": avoid_evening,
        "large_class_threshold": large_class_threshold,
        "lecturer_no_overlap": lecturer_no_overlap,
        "lecturer_preferences": lecturer_prefs,
    }

    return constraints


# =====================================================
# COMBINE MULTIPLE CONSTRAINT TEXTS
# =====================================================

def merge_constraints(hard_text, soft_text):
    """Parse and merge hard + soft constraint texts into one dict.
    
    Hard constraints take precedence for avoid_days / avoid_timeslots.
    Soft constraints contribute morning_preferred, avoid_evening, etc.
    """
    hard = parse_constraints(hard_text) if hard_text.strip() else {}
    soft = parse_constraints(soft_text) if soft_text.strip() else {}

    merged = {
        "avoid_days": sorted(set(hard.get("avoid_days", []) + soft.get("avoid_days", []))),
        "avoid_timeslots": sorted(set(hard.get("avoid_timeslots", []) + soft.get("avoid_timeslots", []))),
        "morning_preferred": hard.get("morning_preferred", False) or soft.get("morning_preferred", False),
        "avoid_evening": hard.get("avoid_evening", False) or soft.get("avoid_evening", False),
        "large_class_threshold": hard.get("large_class_threshold") or soft.get("large_class_threshold"),
        "lecturer_no_overlap": True,
        "lecturer_preferences": {
            **hard.get("lecturer_preferences", {}),
            **soft.get("lecturer_preferences", {})
        },
    }
    return merged


# =====================================================
# SAVE CONSTRAINTS
# =====================================================

def save_constraints(text, filename="constraints.json"):
    """Parse text and save the structured constraint dict to a JSON file."""
    parsed = parse_constraints(text)

    with open(filename, "w") as f:
        json.dump(parsed, f, indent=4)

    return parsed


def save_merged_constraints(hard_text, soft_text, filename="constraints.json"):
    """Parse and merge hard + soft texts, save to JSON file."""
    merged = merge_constraints(hard_text, soft_text)

    with open(filename, "w") as f:
        json.dump(merged, f, indent=4)

    return merged


# =====================================================
# HUMAN-READABLE SUMMARY (for UI display)
# =====================================================

def summarise_constraints(constraints):
    """Return a human-readable list of parsed constraints for display in the UI."""
    lines = []

    if constraints.get("avoid_days"):
        lines.append(f"🚫 No classes on: {', '.join(constraints['avoid_days'])}")

    if constraints.get("morning_preferred"):
        lines.append("☀️  Morning slots preferred (8am–1pm)")

    if constraints.get("avoid_evening"):
        lines.append("🌙 Evening slots avoided (4pm–6pm)")

    if constraints.get("large_class_threshold"):
        lines.append(f"🏛️  Classes with {constraints['large_class_threshold']}+ students → large halls")

    if constraints.get("avoid_timeslots"):
        count = len(constraints["avoid_timeslots"])
        lines.append(f"⏰ {count} specific timeslot(s) excluded")

    lp = constraints.get("lecturer_preferences", {})
    if lp:
        for name, pref in lp.items():
            if pref.get("avoid_day"):
                lines.append(f"👤 {name}: not available on {pref['avoid_day']}")
            if pref.get("prefer_day"):
                lines.append(f"👤 {name}: prefers {pref['prefer_day']}")

    if not lines:
        lines.append("✅ Standard constraints only (no lecturer/room double-booking)")

    return lines


if __name__ == "__main__":
    # Quick test
    test_text = """
    No classes on Saturday.
    Morning classes are preferred.
    Avoid scheduling lectures late on Fridays.
    Large classes above 200 students must use big halls.
    No overlapping classes for lecturers.
    Dr. Adebayo should not teach on Mondays.
    """
    result = parse_constraints(test_text)
    print("Parsed constraints:")
    for k, v in result.items():
        print(f"  {k}: {v}")
    print("\nSummary:")
    for line in summarise_constraints(result):
        print(" ", line)