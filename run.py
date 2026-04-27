import threading
import uvicorn
import subprocess
import time

# ---------------- START BACKEND ----------------
def start_backend():
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)

# ---------------- START FRONTEND ----------------
def start_frontend():
    time.sleep(2)  # wait for backend to start
    subprocess.run(["python", "frontend/app.py"])

# ---------------- RUN BOTH ----------------
if __name__ == "__main__":
    t1 = threading.Thread(target=start_backend)
    t1.start()

    start_frontend()