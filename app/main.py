from fastapi import FastAPI, HTTPException
from app.models import TravelClaim, ClaimDecision
from app.agent import process_claim

app = FastAPI(
    title="Travel Reimbursement Approval Agent",
    description="API for processing and approving travel reimbursement claims.",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/approve-claim", response_model=ClaimDecision)
def approve_claim(claim: TravelClaim):
    try:
        decision = process_claim(claim.model_dump())
        return decision
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
