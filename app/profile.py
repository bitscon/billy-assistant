import os
import json

PROFILE_PATH = os.getenv("PROFILE_PATH", "data/user_profile.json")

def load_profile():
    try:
        with open(PROFILE_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return {"name": "Chad", "style": "formal", "favorites": [], "role": "", "tone": ""}

def save_profile(profile):
    os.makedirs(os.path.dirname(PROFILE_PATH), exist_ok=True)
    with open(PROFILE_PATH, 'w') as f:
        json.dump(profile, f, indent=2)

def get_role():
    return {"role": load_profile().get("role", "")}

def update_profile_role(role):
    profile = load_profile()
    profile["role"] = role
    save_profile(profile)
    return {"status": "role updated"}

def get_tone():
    return {"tone": load_profile().get("tone", "")}

def update_profile_tone(tone):
    profile = load_profile()
    profile["tone"] = tone
    save_profile(profile)
    return {"status": "tone updated"}

def add_favorite(entry):
    profile = load_profile()
    profile.setdefault("favorites", []).append(entry)
    save_profile(profile)
    return {"status": "favorite added", "total": len(profile["favorites"])}

def get_favorites():
    return load_profile().get("favorites", [])
