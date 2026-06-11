import pandas as pd

from lecturer import assign_lecturer

from venue_cleaner import clean_venue

from room_capacities import ROOM_CAPACITY


# ==========================================
# LOAD DATASET
# ==========================================

file_path = "data/cleaned_dataset.csv"

df = pd.read_csv(file_path)

# ==========================================
# CLEAN COLUMN NAMES
# ==========================================

df.columns = (
    df.columns
    .str.strip()
    .str.upper()
)

# ==========================================
# REMOVE EMPTY ROWS
# ==========================================

df = df.dropna(how="all")

# ==========================================
# CLEAN COURSE CODES
# ==========================================

df["COURSE CODE"] = (
    df["COURSE CODE"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# ==========================================
# CLEAN VENUES
# ==========================================

df["CLASSROOM(VENUE)"] = (
    df["CLASSROOM(VENUE)"]
    .apply(clean_venue)
)

# ==========================================
# CLEAN STUDENTS
# ==========================================

df["STUDENTS"] = pd.to_numeric(
    df["STUDENTS"],
    errors="coerce"
)

df["STUDENTS"] = (
    df["STUDENTS"]
    .fillna(0)
    .astype(int)
)

# ==========================================
# ASSIGN LECTURERS
# ==========================================

df["LECTURER"] = (
    df["COURSE CODE"]
    .apply(assign_lecturer)
)

# ==========================================
# GET ROOM CAPACITY
# ==========================================

def get_capacity(venue):

    venue = str(venue).strip()

    return ROOM_CAPACITY.get(
        venue,
        100
    )

# ==========================================
# ADD ROOM CAPACITY
# ==========================================

df["VENUE_CAPACITY"] = (
    df["CLASSROOM(VENUE)"]
    .apply(get_capacity)
)

# ==========================================
# REMOVE INVALID RECORDS
# ==========================================

df = df.dropna(
    subset=["COURSE CODE"]
)

df = df[
    df["COURSE CODE"] != "NAN"
]

# ==========================================
# REMOVE IMPOSSIBLE RECORDS
# ==========================================

df = df[
    df["STUDENTS"] <=
    (df["VENUE_CAPACITY"] * 1.5)
]

# ==========================================
# REMOVE DUPLICATES
# ==========================================

df = df.drop_duplicates()

# ==========================================
# SAVE CLEAN DATASET
# ==========================================

df.to_csv(
    "cleaned_dataset.csv",
    index=False
)

# ==========================================
# SUMMARY
# ==========================================

print("\nDataset cleaned successfully.\n")

print(df.head())

print("\nTOTAL ROWS:", len(df))

print(
    "\nTOTAL LECTURERS:",
    df["LECTURER"].nunique()
)

print(
    "\nTOTAL VENUES:",
    df["CLASSROOM(VENUE)"].nunique()
)

# ==========================================
# SHOW UNKNOWN VENUES
# ==========================================

unknown = df[
    df["VENUE_CAPACITY"] == 100
]["CLASSROOM(VENUE)"].unique()

print("\nUNKNOWN VENUES:\n")

for venue in unknown:
    print(venue)