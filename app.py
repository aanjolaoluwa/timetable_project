# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os
import json
import shutil
import pandas as pd
from typing import List

# Import project files
from database import init_db, SessionLocal, TimetableEntry
from engine import load_dataset, generate_initial_solution, genetic_algorithm, evaluate_timetable
from nlp_parser import save_merged_constraints, parse_constraints, summarise_constraints

app = FastAPI(
    title="AI Timetable Scheduler API",
    description="Backend API for generating and managing academic timetables using AI optimization."
)

# Enable CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite Database on startup
init_db()

# Directory configuration
UPLOAD_DIR = "data"
CONSTRAINTS_FILE = "constraints.json"  # Unified path: always root-level
os.makedirs(UPLOAD_DIR, exist_ok=True)


# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -----------------------------
# HELPER: load constraints from file
# -----------------------------
def _load_constraints():
    """Load constraints.json from the root directory. Returns None if not found."""
    if os.path.exists(CONSTRAINTS_FILE):
        try:
            with open(CONSTRAINTS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return None


# -----------------------------
# ENDPOINT: Upload Raw Dataset
# -----------------------------
@app.post("/api/upload")
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    file_path = os.path.join(UPLOAD_DIR, "cleaned_dataset.csv")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return {"message": "Dataset uploaded successfully", "filename": file.filename}


# -----------------------------
# ENDPOINT: Parse and Save Constraints
# -----------------------------
@app.post("/api/constraints")
async def parse_and_save_constraints(payload: dict):
    """Accept hard + soft constraint text, parse into structured JSON, and save."""
    hard_text = payload.get("hard_text", "")
    soft_text = payload.get("soft_text", "")

    # Also support legacy single "text" field
    if not hard_text and not soft_text:
        combined = payload.get("text", "")
        if not combined.strip():
            raise HTTPException(status_code=400, detail="Constraints text cannot be empty.")
        parsed = parse_constraints(combined)
        with open(CONSTRAINTS_FILE, "w") as f:
            json.dump(parsed, f, indent=4)
    else:
        parsed = save_merged_constraints(hard_text, soft_text, filename=CONSTRAINTS_FILE)

    summary = summarise_constraints(parsed)
    return {
        "message": "Constraints parsed and saved successfully",
        "constraints": parsed,
        "summary": summary
    }


# -----------------------------
# ENDPOINT: Generate Timetable & Save to DB
# -----------------------------
@app.post("/api/generate")
async def run_scheduler(generations: int = 50, db: Session = Depends(get_db)):
    dataset_path = os.path.join(UPLOAD_DIR, "cleaned_dataset.csv")
    if not os.path.exists(dataset_path):
        raise HTTPException(
            status_code=404,
            detail="No dataset uploaded yet. Please upload a CSV first."
        )

    try:
        # 1. Load dataset (unknown lecturers replaced with Nigerian names)
        df = load_dataset(dataset_path)

        # 2. Load parsed constraints (from root constraints.json)
        constraints = _load_constraints()

        # 3. Generate initial solution respecting constraints
        initial_timetable = generate_initial_solution(df, constraints)

        # 4. Run Genetic Algorithm with constraints guiding search
        optimized_timetable, history = genetic_algorithm(
            initial_timetable,
            constraints=constraints,
            generations=generations,
            population_size=20
        )

        # 5. Clear old database entries
        db.query(TimetableEntry).delete()
        db.commit()

        # 6. Persist optimized schedule into SQLite
        for entry in optimized_timetable:
            db_entry = TimetableEntry(
                course=entry["course"],
                lecturer=entry["lecturer"],
                students=entry["students"],
                venue=entry["venue"],
                timeslot=entry["timeslot"],
                duration=entry["duration"],
                level=entry["level"]
            )
            db.add(db_entry)

        db.commit()

        # 7. Final evaluation
        metrics = evaluate_timetable(optimized_timetable, constraints)
        
        # Count how many sessions are still unscheduled
        unscheduled_count = sum(
            1 for e in optimized_timetable if e.get("timeslot") == "UNSCHEDULED"
        )
        scheduled_count = len(optimized_timetable) - unscheduled_count

        return {
            "status": "Success",
            "message": "Timetable generated and saved successfully",
            "total_sessions": len(optimized_timetable),
            "scheduled": scheduled_count,
            "unscheduled": unscheduled_count,
            "generations_run": generations,
            "fitness_history": history[-10:],  # last 10 generations for the UI
            "metrics": metrics
        }

    except Exception as e:
        db.rollback()
        import traceback
        tb = traceback.format_exc()
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}\n{tb}")


# -----------------------------
# ENDPOINT: Retrieve Active Timetable
# -----------------------------
@app.get("/api/timetable")
def get_timetable(db: Session = Depends(get_db)):
    entries = db.query(TimetableEntry).all()
    if not entries:
        return {"message": "No active timetable found. Run generation first.", "data": []}

    data = []
    for entry in entries:
        data.append({
            "course": entry.course,
            "lecturer": entry.lecturer,
            "students": entry.students,
            "venue": entry.venue,
            "timeslot": entry.timeslot,
            "duration": entry.duration,
            "level": entry.level
        })
    return {"total_sessions": len(data), "data": data}


# -----------------------------
# ENDPOINT: Preview Constraint Parsing
# -----------------------------
@app.post("/api/constraints/preview")
async def preview_constraints(payload: dict):
    """Parse constraint text and return human-readable summary without saving."""
    hard_text = payload.get("hard_text", "")
    soft_text = payload.get("soft_text", "")
    combined = payload.get("text", "")

    if hard_text or soft_text:
        from nlp_parser import merge_constraints
        parsed = merge_constraints(hard_text, soft_text)
    elif combined:
        parsed = parse_constraints(combined)
    else:
        raise HTTPException(status_code=400, detail="No constraint text provided.")

    return {
        "parsed": parsed,
        "summary": summarise_constraints(parsed)
    }


# -----------------------------
# ENDPOINT: Welcome Root Route
# -----------------------------
@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "AI Timetable Scheduler API is running.",
        "documentation": "Go to http://127.0.0.1:8000/docs to test the API endpoints."
    }