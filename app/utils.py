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


def get_llm():
    """Factory to create LLM with fallbacks dynamically based on env config."""
    provider = os.getenv("LLM_PROVIDER", "google").lower()
    # Read a comma-separated list of models from the environment
    models_str = os.getenv("LLM_MODELS", "gemini-3.5-flash")
    model_names = [m.strip() for m in models_str.split(",") if m.strip()]
    
    if not model_names:
        raise ValueError("No models specified in LLM_MODELS")
        
    def _create_model(model_name: str):
        if provider == "google":
            from langchain_google_genai import ChatGoogleGenerativeAI
            # We set max_retries=0 so it fails fast on quota limits and triggers the fallback
            return ChatGoogleGenerativeAI(model=model_name, temperature=0, max_retries=0)
        elif provider == "openai":
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(model=model_name, temperature=0, max_retries=0)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
            
    primary_llm = _create_model(model_names[0])
    
    fallbacks = []
    for model_name in model_names[1:]:
        fallbacks.append(_create_model(model_name))
        
    if fallbacks:
        return primary_llm.with_fallbacks(fallbacks)
    return primary_llm
