"""
tools.py

Four core tools used by the Travel Reimbursement Approval Agent.
Each tool is a pure Python function with a clear, single responsibility.
These are wrapped as LangChain Tool objects in agent.py.
"""

from app.utils import load_policy_text, load_limits, load_submitted_claims


REQUIRED_FIELDS = ["claim_id", "employee_id", "date", "amount",
                    "category", "vendor", "receipt_attached"]


def policy_lookup(category: str) -> str:
    """
    Tool 1: Look up the relevant policy text for a given expense category.
    Returns a plain text snippet describing limits/rules for that category.
    """
    policy_text = load_policy_text()
    category = category.lower().strip()

    section_map = {
        "meal": "## 1. Meal Allowance",
        "hotel": "## 2. Hotel Accommodation",
        "transport": "## 3. Local Transport",
        "flight": "## 4. Air Travel",
    }

    if category in section_map:
        marker = section_map[category]
        start = policy_text.find(marker)
        end = policy_text.find("\n## ", start + 1)
        section = policy_text[start:end if end != -1 else None]
        return section.strip()

    return (
        f"No standard policy found for category '{category}'. "
        "This falls under Miscellaneous / Other Categories and "
        "requires Manual Review regardless of amount."
    )


def receipt_completeness_check(claim: dict) -> dict:
    """
    Tool 2: Verify that a claim has all required fields populated.
    Returns: {"complete": bool, "missing_fields": [list of field names]}
    """
    missing = []
    for field in REQUIRED_FIELDS:
        value = claim.get(field, None)
        if value is None or value == "":
            missing.append(field)

    if claim.get("amount", 0) > 200 and claim.get("receipt_attached") is not True:
        if "receipt_attached" not in missing:
            missing.append("receipt_attached")

    return {
        "complete": len(missing) == 0,
        "missing_fields": missing
    }


def threshold_validator(category: str, amount: float, city: str = "") -> dict:
    """
    Tool 3: Check if the claimed amount is within the approved limit
    for its category (and city, for hotel claims).
    Returns: {"within_limit": bool, "limit": float, "excess": float}
    """
    limits = load_limits()
    category = category.lower().strip()
    city = (city or "").lower().strip()

    if category == "hotel":
        cfg = limits["hotel"]
        is_metro = city in cfg["metro_cities"]
        limit = cfg["metro_limit"] if is_metro else cfg["non_metro_limit"]

    elif category == "meal":
        limit = limits["meal"]["daily_limit"]

    elif category == "transport":
        limit = limits["transport"]["taxi_limit"]

    else:
        return {"within_limit": False, "limit": None, "excess": None,
                "note": "No standard limit defined for this category."}

    excess = max(0, amount - limit)
    return {
        "within_limit": amount <= limit,
        "limit": limit,
        "excess": excess
    }


def duplicate_detector(employee_id: str, date: str, amount: float) -> dict:
    """
    Tool 4: Check whether an identical claim (same employee, date, amount)
    has already been submitted previously.
    Returns: {"is_duplicate": bool, "original_claim_id": str | None}
    """
    submitted = load_submitted_claims()
    for c in submitted:
        if (c["employee_id"] == employee_id and
                c["date"] == date and
                float(c["amount"]) == float(amount)):
            return {"is_duplicate": True, "original_claim_id": c["claim_id"]}

    return {"is_duplicate": False, "original_claim_id": None}
