import json
import os
import time
from app.agent import process_claim
from app.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
INPUT_FILE = os.path.join(SAMPLES_DIR, "sample_claims.json")
OUTPUT_FILE = os.path.join(SAMPLES_DIR, "sample_outputs.json")

def main():
    logger.info(f"Loading claims from {INPUT_FILE}...")
    print(f"Loading claims from {INPUT_FILE}...")
    with open(INPUT_FILE, "r") as f:
        claims = json.load(f)

    results = []
    
    for claim in claims:
        print(f"\nProcessing Claim ID: {claim.get('claim_id')}...")
        try:
            decision = process_claim(claim)
            print(f"Result for {claim.get('claim_id')}: {decision.decision}")
            logger.info(f"Successfully processed {claim.get('claim_id')} with result {decision.decision}")
            results.append(decision.model_dump())
        except Exception as e:
            print(f"Error processing {claim.get('claim_id')}: {e}")
            logger.error(f"Error processing {claim.get('claim_id')}: {e}")
            
        # Add a delay to prevent hitting the free-tier API rate limits
        import time
        time.sleep(30)
            
    logger.info(f"Saving results to {OUTPUT_FILE}...")
    print(f"\nSaving results to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2)
        
    logger.info("Done processing all claims.")
    print("Done!")

if __name__ == "__main__":
    main()

