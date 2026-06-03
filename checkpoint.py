import os
import json

CHECKPOINT_FILE = 'checkpoint.json'

def save_checkpoint(step, status):
    data = load_checkpoint()
    data[step] = status
    with open(CHECKPOINT_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def load_checkpoint():
    if not os.path.exists(CHECKPOINT_FILE):
        return {}
    try:
        with open(CHECKPOINT_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
