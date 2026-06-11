import random
from academic_data import LECTURERS

# ---------------------------------
# COURSE PREFIX TO DEPARTMENT
# ---------------------------------

COURSE_DEPARTMENT_MAP = {
    "ACC": "ACCOUNTING",
    "ARC": "ARCHITECTURE",
    "BCH": "BIOCHEMISTRY",
    "BIO": "BIOLOGICAL_SCIENCES",
    "BMS": "BUSINESS_MANAGEMENT",
    "BNF": "BANKING_AND_FINANCE",
    "CHE": "CHEMICAL_ENGINEERING",
    "CHM": "CHEMISTRY",
    "CSC": "COMPUTER_AND_INFORMATION_SCIENCES",
    "CIS": "COMPUTER_AND_INFORMATION_SCIENCES",
    "IFT": "COMPUTER_AND_INFORMATION_SCIENCES",
    "CVE": "CIVIL_ENGINEERING",
    "ECO": "ECONOMICS_AND_DEVELOPMENT_STUDIES",
    "EEE": "ELECTRICAL_ENGINEERING",
    "EST": "ESTATE_MANAGEMENT",
    "MAC": "MASS_COMMUNICATION",
    "MTH": "MATHEMATICS",
    "MAT": "MATHEMATICS",
    "MEE": "MECHANICAL_ENGINEERING",
    "PET": "PETROLEUM_ENGINEERING",
    "POL": "POLITICAL_SCIENCE_AND_IR",
    "PSY": "PSYCHOLOGY",
    "SOC": "SOCIOLOGY",
    "ENG": "LANGUAGES",
    "LAN": "LANGUAGES",
}

# =========================
# ASSIGN LECTURER
# =========================
def assign_lecturer(course_code):

    # HANDLE EMPTY VALUES
    if course_code is None:
        return "Unknown Lecturer"

    # CONVERT TO STRING
    course_code = str(course_code)

    # REMOVE SPACES
    course_code = course_code.strip().upper()

    # HANDLE NaN
    if course_code == "NAN":
        return "Unknown Lecturer"

    # EXTRACT PREFIX
    prefix = ""

    for char in course_code:
        if char.isalpha():
            prefix += char
        else:
            break

    # FIND DEPARTMENT
    department = COURSE_DEPARTMENT_MAP.get(prefix)

    if not department:
        return "Unknown Lecturer"

    lecturers = LECTURERS.get(department, [])

    if not lecturers:
        return "Unknown Lecturer"

    return random.choice(lecturers)

# =========================
# FUNCTIONS
# =========================

def get_all_lecturers():
    return [
        lecturer
        for dept in LECTURERS.values()
        for lecturer in dept
    ]


def get_department(name):
    return LECTURERS.get(
        name.upper(),
        []
    )