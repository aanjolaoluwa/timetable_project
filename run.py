import subprocess
import sys
import time

def main():
    print("Starting AI Timetable Scheduler...")
    
    # Start the FastAPI backend
    print("Starting backend server (FastAPI) on http://127.0.0.1:8000 ...")
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    
    # Give the backend a few seconds to start up
    time.sleep(3)
    
    # Start the Streamlit frontend
    print("Starting frontend (Streamlit)...")
    frontend_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app_ui.py"]
    )
    
    try:
        # Wait for processes
        frontend_process.wait()
        backend_process.wait()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        frontend_process.terminate()
        backend_process.terminate()
        frontend_process.wait()
        backend_process.wait()
        print("Shutdown complete.")

if __name__ == "__main__":
    main()
