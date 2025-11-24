from google import genai
from pydantic import BaseModel, Field
from typing import Optional
import os
from dotenv import load_dotenv
import json
import typer
from tqdm import tqdm


load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


class VerificationResult(BaseModel):
    is_valid: bool = Field(
        description="True if the candidate is a VC fund founded approximately 7-12 years ago with an active portfolio."
    )
    founding_year: Optional[str] = Field(description="The founding year of the fund.")
    reason: str = Field(description="Reasoning for the verification result.")


def verify_candidate(client: genai.Client, candidate: dict) -> dict:
    name = candidate.get("name", "Unknown")
    description = candidate.get("description", "")
    url = candidate.get("url", "")

    prompt = f"""
    Verify if the following candidate is a Venture Capital fund that fits these criteria:
    1. Founded between 7 and 12 years ago.
    2. Has an active private portfolio.
    3. Has pressure for liquidity (e.g., approaching end of fund life).

    Candidate: {name}
    URL: {url}
    Description: {description}
    Full candidate: {candidate}
    """

    try:
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=prompt,
            config={
                "tools": [{"google_search": {}}, {"url_context": {}}],
                "response_mime_type": "application/json",
                "response_schema": VerificationResult,
            },
        )

        verification = VerificationResult.model_validate_json(response.text)
        candidate["verification"] = verification.model_dump()
        print(f"Verified: {name} - Valid: {verification.is_valid}")

    except Exception as e:
        print(f"Error verifying {name}: {e}")
        candidate["verification"] = {
            "is_valid": False,
            "reason": str(e),
            "founding_year": None,
        }

    return candidate


def main(
    input_file: str = "results-simple-base.json",
    output_file: str = "verified_candidates.json",
):
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found. Trying 'matched.json'...")
        input_file = "matched.json"
        if not os.path.exists(input_file):
            print(f"File {input_file} not found.")
            return

    with open(input_file, "r") as f:
        data = json.load(f)

    candidates = data.get("candidates", []) if isinstance(data, dict) else data
    if not isinstance(candidates, list):
        print(
            "Invalid input format: expected a list of candidates or a dict with 'candidates' key."
        )
        return

    verified_results = []
    verified_ids = set()

    if os.path.exists(output_file):
        try:
            with open(output_file, "r") as f:
                verified_results = json.load(f)
                verified_ids = {
                    c.get("candidate_id")
                    for c in verified_results
                    if c.get("candidate_id")
                }
            print(
                f"Loaded {len(verified_results)} verified candidates from {output_file}"
            )
        except Exception as e:
            print(f"Error reading {output_file}, starting fresh: {e}")

    print(f"Verifying {len(candidates)} candidates from {input_file}...")

    for candidate in tqdm(candidates):
        if candidate.get("candidate_id") in verified_ids:
            continue

        result = verify_candidate(client, candidate)
        verified_results.append(result)

        with open(output_file, "w") as f:
            json.dump(verified_results, f, indent=2)

    print(f"Saved verified candidates to {output_file}")


if __name__ == "__main__":
    typer.run(main)
