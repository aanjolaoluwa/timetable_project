# data_preparer.py
import sys
import os

# Ensure parent directory is in path for imports
sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import pandas as pd
import random
from academic_data import LECTURERS, COURSE_CODES

# -----------------------------
# LOAD DATASET
# -----------------------------
def load_dataset(file_path):
    df = pd.read_csv(file_path, encoding="latin1")
    # Clean column names
    df.columns = [col.strip() for col in df.columns]
    return df


# -----------------------------
# CLEAN LEVEL (ROBUST VERSION)
# -----------------------------
def clean_level(level):
    """
    Standardizes messy values like '400/200', '400 & 300', '4400', etc.
    """
    if pd.isna(level):
        return 100

    level_str = str(level).strip().replace(" ", "")
    
    # Handle composite levels
    for separator in ["/", "&"]:
        if separator in level_str:
            level_str = level_str.split(separator)[0]
            
    try:
        val = int(level_str)
        # Handle typo outliers (e.g., "4400" -> 400, "2200" -> 200)
        if val > 600:
            val = int(str(val)[0] + "00")
        return val
    except ValueError:
        return 100


# -----------------------------
# GENERATE COURSE TITLE
# -----------------------------
def generate_course_title(course_code):
    course_code = str(course_code)
    if course_code.startswith("CSC"):
        return "Computer Science Course"
    elif course_code.startswith("EEE"):
        return "Engineering Course"
    elif course_code.startswith("GST"):
        return "General Studies Course"
    else:
        return "University Course"


# -----------------------------
# STUDENT GENERATION LOGIC
# -----------------------------
department_weights = {
    "CSC": 1.5,
    "EEE": 1.3,
    "MEE": 1.2,
    "BUS": 1.2,
    "ACC": 1.1,
    "BIO": 0.6,
    "CHE": 0.7,
    "PHY": 0.8,
    "GST": 2.0
}

def base_students(level):
    level = clean_level(level)
    if level == 100:
        return 250
    elif level == 200:
        return 180
    elif level == 300:
        return 120
    elif level == 400:
        return 80
    else:
        return 100


def generate_students(course_code, level):
    base = base_students(level)
    dept = str(course_code)[:3]
    weight = department_weights.get(dept, 1.0)
    students = int(base * weight * random.uniform(0.8, 1.2))
    return students


# -----------------------------
# SAFE NUMERIC CONVERSION (FOR HOURS)
# -----------------------------
def safe_int(value, default=2):
    try:
        return int(value)
    except:
        return default


# -----------------------------
# DETECT DEPARTMENT
# -----------------------------
def detect_department(course_code):
    course_code = str(course_code).upper().strip()
    # Remove spaces and hyphens
    course_code = (
        course_code
        .replace(" ", "")
        .replace("-", "")
    )

    prefixes = {
        "ACC": "ACCOUNTING",
        "ARC": "ARCHITECTURE",
        "BCH": "BIOCHEMISTRY",
        "BIO": "BIOLOGICAL_SCIENCES",
        "BMS": "BUSINESS_MANAGEMENT",
        "BNF": "BANKING_AND_FINANCE",
        "CHE": "CHEMICAL_ENGINEERING",
        "CHM": "CHEMISTRY",
        "CSC": "COMPUTER_AND_INFORMATION_SCIENCES",
        "CVE": "CIVIL_ENGINEERING",
        "ECO": "ECONOMICS_AND_DEVELOPMENT_STUDIES",
        "EEE": "ELECTRICAL_ENGINEERING",
        "EST": "ESTATE_MANAGEMENT",
        "MAC": "MASS_COMMUNICATION",
        "MTH": "MATHEMATICS",
        "MEE": "MECHANICAL_ENGINEERING",
        "PET": "PETROLEUM_ENGINEERING",
        "POL": "POLITICAL_SCIENCE_AND_IR",
        "PSY": "PSYCHOLOGY",
        "SOC": "SOCIOLOGY",
        "ENG": "LANGUAGES",
        "LAN": "LANGUAGES",
        "PHY": "PHYSICS"
    }

    for prefix, department in prefixes.items():
        if course_code.startswith(prefix):
            return department

    return None


# -----------------------------
# GENERATE LECTURERS
# -----------------------------
def generate_lecturer(course_code):
    department = detect_department(course_code)
    if department is None:
        return "Unknown Lecturer"

    lecturers = LECTURERS.get(department, [])
    if len(lecturers) == 0:
        return "Unknown Lecturer"

    return random.choice(lecturers)


# -----------------------------
# PREPARE DATASET
# -----------------------------
def prepare_dataset(file_path):
    df = load_dataset(file_path)

    # Ensure required columns exist
    if "COURSE CODE" not in df.columns or "LEVEL" not in df.columns:
        raise ValueError("Dataset must contain 'COURSE CODE' and 'LEVEL' columns")

    # Generate missing columns
    df["COURSE TITLE"] = df["COURSE CODE"].apply(generate_course_title)
    df["LECTURER"] = df["COURSE CODE"].apply(generate_lecturer)
    df["STUDENTS"] = df.apply(
        lambda row: generate_students(row["COURSE CODE"], row["LEVEL"]),
        axis=1
    )

    # Generate units from hours (if available)
    if "COURSE LOAD(HOURS)" in df.columns:
        df["COURSE LOAD(HOURS)"] = df["COURSE LOAD(HOURS)"].apply(safe_int)
        df["COURSE UNIT"] = df["COURSE LOAD(HOURS)"].apply(
            lambda x: 2 if x <= 2 else 3
        )
    
    # Drop useless column if it exists
    if "NO OF STUDENT PER COURSE" in df.columns:
        df = df.drop(columns=["NO OF STUDENT PER COURSE"])

    return df


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    file_path = "data/combined_dataset_clean.csv"
    df = prepare_dataset(file_path)

    print("\n=== CLEANED DATASET ===")
    print(df.head())
    print("\nTotal rows:", len(df))

    # Save final dataset
    df.to_csv("data/final_dataset.csv", index=False)
    print("\nSaved as final_dataset.csv")