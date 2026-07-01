from pydantic import BaseModel, Field
from typing import Optional, List


class TravelClaim(BaseModel):
    claim_id: str
    employee_id: str
    employee_name: str
    date: str
    category: str
    amount: float
    vendor: str
    city: Optional[str] = ""
    receipt_attached: bool
    description: Optional[str] = ""


class ClaimDecision(BaseModel):
    claim_id: str
    decision: str  # APPROVED | PARTIALLY_APPROVED | REJECTED | MANUAL_REVIEW
    approved_amount: float
    requested_amount: float
    deducted_amount: float
    missing_documents: List[str] = Field(default_factory=list)
    policy_reference: str
    confidence: str  # HIGH | MEDIUM | LOW
    explanation: str
    manual_review_reason: Optional[str] = None
    tools_used: List[str] = Field(default_factory=list)
