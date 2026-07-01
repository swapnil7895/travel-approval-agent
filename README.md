# Travel Reimbursement Approval Agent

This is a working prototype of an AI-assisted Travel Reimbursement Approval Agent. It reviews employee travel reimbursement claims against policy, receipts, limits, and approval rules, and returns a structured recommendation.

## Setup Instructions

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd travel-approval-agent
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    # On Windows:
    venv\Scripts\activate
    # On macOS/Linux:
    # source venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Copy `.env.example` to `.env` and configure your API keys and models:
    ```
    LLM_PROVIDER=google
    LLM_MODELS=gemini-3.5-flash,gemini-2.5-flash
    GOOGLE_API_KEY=your_gemini_api_key
    ```

## How to Run

### Option 1: Run via CLI (Batch Processing)
To process the sample claims provided in `samples/sample_claims.json` and save the outputs to `samples/sample_outputs.json`, run:
```bash
python cli.py
```

### Option 2: Run via FastAPI (Interactive API)
To start the API server:
```bash
uvicorn app.main:app --reload
```
- Open http://127.0.0.1:8000/docs to access the Swagger UI.
- Use the `/approve-claim` endpoint to POST a new claim and get the decision.
- Use the `/health` endpoint to check if the server is running.

## Design Choices & Architecture

- **LLM Choice & Fallbacks:** The app uses a dynamic LLM Factory (`app/utils.py`) that is completely provider-agnostic. It reads a comma-separated list of models from `.env` (e.g., `gemini-3.5-flash,gemini-2.5-flash`), sets the first as the primary, and automatically configures the rest as fallback models to seamlessly route around strict free-tier rate limits.
- **Agent Framework:** Built using LangGraph's modern `create_react_agent`. It allows the agent to iteratively determine which tool to use based on the tool descriptions and the system prompt, providing far more reliability than older agent types.
- **Data Storage:** Kept it lightweight with local JSON files as requested. This avoids the overhead of setting up a database for a prototype.
- **Validation:** Pydantic models (`ClaimDecision`) ensure strict validation of inputs and outputs, which is critical for structured data tasks.

## Trade-offs

- **Strict Schema Enforcement:** While Pydantic helps, ReAct agents sometimes struggle to perfectly format the final output as raw JSON (often adding conversational text). We implemented a robust Regular Expression extraction to pull the JSON block out of the model's string, preventing `JSONDecodeErrors`. In a production environment, OpenAI's strict function calling or LangChain's `with_structured_output` would be natively integrated.
- **Stateless Tools:** The tools are pure functions that read from the file system. In a highly concurrent production setting, this would cause race conditions (especially with duplicate checking and state).

## Assumptions & Limitations

- **Currency:** Assumes all amounts are in INR (₹) as per the policy.
- **Date format:** Assumes dates are consistently formatted (`YYYY-MM-DD`).
- **File System:** Assumes the script is run from the project root directory so that relative paths to `data/` and `samples/` resolve correctly.
- **Receipt Validation:** Currently, receipt validation just checks a boolean flag (`receipt_attached`). In a real system, it would involve OCR and comparing the receipt data against the claim data.

## Future Improvements

1.  **Structured Output Agent:** Transition to a newer LangChain agent type (like `StructuredChatAgent` or tool calling agents) that inherently supports complex JSON return schemas to avoid manual string stripping.
2.  **Database Integration:** Replace JSON files with a real database (e.g., PostgreSQL or MongoDB) for concurrency support and complex querying.
3.  **OCR Integration:** Implement actual receipt parsing using an OCR library or a vision model (like Gemini 1.5 Pro) to extract line items and verify amounts automatically.
4.  **Unit Tests:** Add comprehensive unit testing using `pytest` for the tools and the agent logic.
