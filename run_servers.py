import subprocess
import sys
import time
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("Starting College Event Management & Recommendation System...")
print("FastAPI Backend running at: http://127.0.0.1:8000")
print("Swagger API Docs at: http://127.0.0.1:8000/docs")
print("Streamlit Web App at: http://localhost:8501")

backend_proc = subprocess.Popen(
    [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", "8000"],
    cwd=BASE_DIR
)

# Wait 2 seconds for backend to start
time.sleep(2)

frontend_proc = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501", "--server.headless", "true"],
    cwd=BASE_DIR
)

try:
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    backend_proc.terminate()
    frontend_proc.terminate()
    print("Servers stopped.")
