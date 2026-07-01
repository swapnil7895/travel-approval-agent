import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import Tool
from app.tools import policy_lookup, receipt_completeness_check, threshold_validator, duplicate_detector
from app.models import ClaimDecision
from dotenv import load_dotenv

load_dotenv()

from app.utils import get_llm
from app.logger import get_logger

logger = get_logger(__name__)

# Initialize the LLM using our dynamic factory
llm = get_llm()

def receipt_check_wrapper(claim_json: str) -> str:
    claim = json.loads(claim_json)
    res = receipt_completeness_check(claim)
    return json.dumps(res)

def threshold_validator_wrapper(args_json: str) -> str:
    args = json.loads(args_json)
    res = threshold_validator(args.get("category", ""), args.get("amount", 0.0), args.get("city", ""))
    return json.dumps(res)

def duplicate_detector_wrapper(args_json: str) -> str:
    args = json.loads(args_json)
    res = duplicate_detector(args.get("employee_id", ""), args.get("date", ""), args.get("amount", 0.0))
    return json.dumps(res)

# Wrap tools
tools = [
    Tool(
        name="PolicyLookup",
        func=policy_lookup,
        description="Useful for looking up the travel policy rules for an expense category. Input should be the category string."
    ),
    Tool(
        name="ReceiptCheck",
        func=receipt_check_wrapper,
        description="Useful to verify if a claim has all required fields populated. Input should be the full claim JSON string."
    ),
    Tool(
        name="ThresholdValidator",
        func=threshold_validator_wrapper,
        description="Useful for checking if the amount is within limit. Input should be a JSON string like {\"category\": \"...\", \"amount\": 100, \"city\": \"...\"}."
    ),
    Tool(
        name="DuplicateDetector",
        func=duplicate_detector_wrapper,
        description="Useful for checking if a claim is a duplicate. Input should be a JSON string like {\"employee_id\": \"...\", \"date\": \"...\", \"amount\": 100}."
    )
]

system_message = """You are a Travel Reimbursement Approval Agent. Your job is to review employee travel reimbursement claims and output a final decision.
You must follow this exact 5-step decision logic:
Step 1: Receipt Completeness Check
Use ReceiptCheck. If a required field is missing or there is no receipt for an amount > 200, the decision will be REJECTED (if receipt missing) or MANUAL_REVIEW (if a minor field is missing).

Step 2: Duplicate Check
Use DuplicateDetector. If the same employee, date, and amount already exists, the decision is REJECTED.

Step 3: Policy Lookup
Use PolicyLookup to fetch relevant policy text for the claim's category.

Step 4: Threshold Validation
Use ThresholdValidator to check the amount against the limits.
- Amount <= limit -> APPROVED (full amount)
- Amount > limit -> PARTIALLY_APPROVED (approved = limit, deducted = excess)
- Amount > 2x limit -> MANUAL_REVIEW
- Category not in policy -> MANUAL_REVIEW

Step 5: Output
Combine the findings and output a structured JSON decision. The output MUST exactly match this JSON schema (NO markdown formatting, just raw JSON):
{
  "claim_id": "str",
  "decision": "APPROVED | PARTIALLY_APPROVED | REJECTED | MANUAL_REVIEW",
  "approved_amount": float,
  "requested_amount": float,
  "deducted_amount": float,
  "missing_documents": ["list of missing fields or empty"],
  "policy_reference": "str (short snippet of policy rule applied)",
  "confidence": "HIGH | MEDIUM | LOW",
  "explanation": "str (plain-English explanation of decision)",
  "manual_review_reason": "str | null",
  "tools_used": ["list of tools used"]
}
"""

agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=system_message,
    debug=False  # Enables an audit trail of reasoning and tool calls in the terminal
)

def process_claim(claim_dict: dict) -> ClaimDecision:
    claim_id = claim_dict.get("claim_id", "UNKNOWN")
    logger.info(f"Starting to process claim ID: {claim_id}")
    input_text = f"Process this claim and return ONLY the JSON result according to your instructions: {json.dumps(claim_dict)}"
    
    result = agent.invoke({"messages": [("user", input_text)]})
    response = result["messages"][-1].content
    
    if isinstance(response, list):
        # Extract text if the content is a list of blocks
        response = "".join(part.get("text", "") if isinstance(part, dict) else str(part) for part in response)
        
    # Clean up response to ensure it's valid JSON
    import re
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if not match:
        logger.error(f"Agent returned no valid JSON for claim ID: {claim_id}. Raw response: {response[:200]}")
        raise ValueError(
            "The AI agent did not return a valid decision. "
            "This is usually caused by an API quota limit. Please wait a moment and try again."
        )

    decision_dict = json.loads(match.group(0))
    logger.info(f"Finished processing claim ID: {claim_id} with decision: {decision_dict.get('decision')}")
    return ClaimDecision(**decision_dict)
