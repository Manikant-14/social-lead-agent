import json
import os
from datetime import datetime

LEADS_FILE = os.path.join(os.path.dirname(__file__), "leads", "leads.json")

def mock_lead_capture(name: str, email: str, platform: str) -> dict:
    lead = {
        "name": name,
        "email": email,
        "platform": platform,
        "captured_at": datetime.utcnow().isoformat() + "Z",
    }

    os.makedirs(os.path.dirname(LEADS_FILE), exist_ok=True)

    existing = []
    if os.path.exists(LEADS_FILE):
        with open(LEADS_FILE, "r") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

    existing.append(lead)

    with open(LEADS_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"Lead captured successfully: {name}, {email}, {platform}")
    return {"status": "success", "lead": lead}


def get_all_leads() -> list:
    if not os.path.exists(LEADS_FILE):
        return []
    with open(LEADS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
