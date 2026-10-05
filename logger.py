# logger.py

import datetime
import os

LOG_FILE = "logs/aimbot_log.txt"
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")

if __name__ == "__main__":
    log("Prueba de logger.")
