import pandas as pd

# LOAD DATASET
df = pd.read_csv("cleaned_dataset.csv")

# SHOW COLUMNS
print(df.columns)

print("\nFIRST 10 ROWS:\n")

print(
    df[
        [
            "COURSE CODE",
            "LECTURER",
            "CLASSROOM(VENUE)",
            "VENUE_CAPACITY",
            "STUDENTS"
        ]
    ].head(10)
)

print("\nUNIQUE LECTURERS:\n")

print(df["LECTURER"].unique()[:30])

print(f"\nTOTAL LECTURERS: {df['LECTURER'].nunique()}")