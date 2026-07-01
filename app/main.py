from fastapi import FastAPI, HTTPException
from app.models import TravelClaim, ClaimDecision
from app.agent import process_claim
from app.logger import get_logger

logger = get_logger(__name__)

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
    logger.info(f"API request to approve claim ID: {claim.claim_id}")
    try:
        decision = process_claim(claim.model_dump())
        logger.info(f"API successfully processed claim ID: {claim.claim_id}")
        return decision
    except Exception as e:
        logger.error(f"API error processing claim ID {claim.claim_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
