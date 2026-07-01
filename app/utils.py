import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")


def load_policy_text() -> str:
    """Load the raw travel policy markdown text."""
    path = os.path.join(DATA_DIR, "travel_policy.md")
    with open(path, "r") as f:
        return f.read()


def load_limits() -> dict:
    """Load approval limits config."""
    path = os.path.join(DATA_DIR, "approval_limits.json")
    with open(path, "r") as f:
        return json.load(f)


def load_submitted_claims() -> list:
    """Load previously submitted claims (for duplicate detection)."""
    path = os.path.join(DATA_DIR, "submitted_claims.json")
    with open(path, "r") as f:
        return json.load(f)


def save_submitted_claim(claim_id: str, employee_id: str, date: str, amount: float):
    """Append a newly processed claim to the submitted claims store."""
    path = os.path.join(DATA_DIR, "submitted_claims.json")
    claims = load_submitted_claims()
    claims.append({
        "claim_id": claim_id,
        "employee_id": employee_id,
        "date": date,
        "amount": amount
    })
    with open(path, "w") as f:
        json.dump(claims, f, indent=2)
