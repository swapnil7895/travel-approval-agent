import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.models import TravelClaim, ClaimDecision
from app.agent import process_claim
from app.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Travel Reimbursement Approval Agent",
    description="API for processing and approving travel reimbursement claims.",
    version="1.0.0"
)

# Serve the chat UI from app/static/
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def serve_ui():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

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
        msg = str(e).split("\n")[0]  # Only the first line — avoids Pydantic multi-line dumps
        logger.error(f"API error processing claim ID {claim.claim_id}: {e}")
        raise HTTPException(status_code=500, detail=msg)
