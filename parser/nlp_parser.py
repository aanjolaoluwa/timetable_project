# nlp_parser.py
import re
import json

def save_constraints(text):
    """
    Rudimentary NLP parser extracting specific restrictions from user input.
    """
    constraints = {
        "avoid_days": [],
        "lecturer_preferences": {},
        "venue_restrictions": {}
    }
    
    lines = text.lower().split("\n")
    days_list = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]
    
    for line in lines:
        # Match day restriction (e.g., "No classes on Friday")
        for day in days_list:
            if "no class" in line and day in line:
                constraints["avoid_days"].append(day.capitalize())
        
        # Match Lecturer restriction (e.g., "Dr. Rotimi cannot teach on Monday")
        lecturer_match = re.search(r"([a-z\.\s]+)\scannot\steach\son\s([a-z]+)", line)
        if lecturer_match:
            lecturer = lecturer_match.group(1).strip().title()
            day = lecturer_match.group(2).strip().capitalize()
            constraints["lecturer_preferences"][lecturer] = {"avoid_day": day}
            
    # Save parsed configuration state
    with open("data/constraints.json", "w") as f:
        json.dump(constraints, f)
        
    return constraints