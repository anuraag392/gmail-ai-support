import json
import os
from app.config.config import PROCESSED_IDS_FILE

STARTUP_FILE = "startup_state.json"


# --------------------------
# Processed IDs (normal use)
# --------------------------
def load_processed_ids():
    if not os.path.exists(PROCESSED_IDS_FILE):
        return set()
    try:
        with open(PROCESSED_IDS_FILE, "r") as f:
            data = json.load(f)
            return set(data)
    except:
        return set()


def save_processed_ids(ids: set):
    with open(PROCESSED_IDS_FILE, "w") as f:
        json.dump(list(ids), f)


# --------------------------
# Startup last message logic
# --------------------------
def get_startup_last_id():
    if not os.path.exists(STARTUP_FILE):
        return None
    try:
        with open(STARTUP_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_message_id")
    except:
        return None


def save_startup_last_id(msg_id):
    with open(STARTUP_FILE, "w") as f:
        json.dump({"last_message_id": msg_id}, f)
