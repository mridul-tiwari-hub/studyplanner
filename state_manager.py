import os
import json
from datetime import datetime

STATE_FILE = "study_state.json"

def load_state():
    """Load study state from the local JSON file. If it doesn't exist, return a default empty state."""
    if not os.path.exists(STATE_FILE):
        return get_default_state()
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
            # Ensure all keys exist
            default = get_default_state()
            for key in default:
                if key not in state:
                    state[key] = default[key]
            return state
    except Exception as e:
        # If file is corrupted or error occurs, return default
        return get_default_state()

def get_default_state():
    """Return default empty state configuration."""
    return {
        "goal": "",
        "syllabus": [],
        "current_day": 1,
        "quiz_history": [],
        "agent_logs": [],
        "generated_lessons": {},
        "generated_quizzes": {}
    }

def save_state(state):
    """Save the state dictionary back to the local JSON file."""
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"Error saving state: {e}")

def reset_state():
    """Clear study state file and return a clean default state."""
    state = get_default_state()
    save_state(state)
    return state

def log_agent_thought(agent_name, message):
    """Append a log entry for an agent thought/communication to the state and save it."""
    state = load_state()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    state["agent_logs"].append({
        "timestamp": timestamp,
        "agent": agent_name,
        "message": message
    })
    save_state(state)

def update_day_status(day_num, status):
    """Update status of a day in the syllabus ('locked', 'active', 'completed', 'review')."""
    state = load_state()
    for day in state["syllabus"]:
        if day["day"] == day_num:
            day["status"] = status
    save_state(state)
