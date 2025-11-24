from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
import typer
import json
from collections import Counter
from PIL import Image

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)


def generate_visualization(
    candidates: list, genai_client: genai.Client = None
) -> Image.Image | None:
    if genai_client is None:
        genai_client = client

    total = len(candidates)
    valid_count = 0
    invalid_count = 0
    founding_years = []

    for candidate in candidates:
        verification = candidate.get("verification", {})
        if verification.get("is_valid"):
            valid_count += 1
            year = verification.get("founding_year")
            if year:
                year_str = str(year).strip()[:4]
                if year_str.isdigit():
                    founding_years.append(year_str)
        else:
            invalid_count += 1

    top_years = Counter(founding_years).most_common(5)

    prompt = f"""
    Generate a clean, professional infographic visualizing these Venture Capital verification results:
    
    - Total Candidates: {total}
    - Valid Funds (Founding window ~8-12 years): {valid_count}
    - Invalid/Unmatched: {invalid_count}
    - Top Founding Years: {top_years}
    
    Use a modern business style with clear charts (pie chart for status, bar chart for years).
    """

    print(f"Generating visualization for {total} candidates...")

    response = genai_client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            image_config=types.ImageConfig(aspect_ratio="16:9", image_size="4K")
        ),
    )

    image_parts = [part for part in response.parts if part.inline_data]

    if image_parts:
        return image_parts[0].as_image()
    return None


def main(
    input_file: str = "verified_candidates.json",
    output_image: str = "visualization.png",
):
    if not os.path.exists(input_file):
        print(f"Input file {input_file} not found.")
        return

    with open(input_file, "r") as f:
        data = json.load(f)

    candidates = data.get("candidates", []) if isinstance(data, dict) else data

    try:
        image = generate_visualization(candidates, client)
        if image:
            image.save(output_image)
            print(f"Saved visualization to {output_image}")
        else:
            print("No image generated in response.")
    except Exception as e:
        print(f"Error generating image: {e}")


if __name__ == "__main__":
    typer.run(main)
