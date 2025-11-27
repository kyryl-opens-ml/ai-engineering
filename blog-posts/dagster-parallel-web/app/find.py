import json
import time
from pathlib import Path
import os
import requests
import typer
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PARALLEL_API_KEY")

BASE_URL = "https://api.parallel.ai/v1beta"
HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json",
    "parallel-beta": "findall-2025-09-15",
}

SCHEMA = {
    "objective": "Find all venture capital funds close to 10 years window",
    "entity_type": "venture_capital_funds",
    "match_conditions": [
        {
            "name": "founded_between_8_12_years_ago_check",
            "description": "Venture capital fund must have been founded between 8 and 12 years ago from the current date. If the founding date is unavailable, return not_sure.",
        },
    ],
    "generator": "base",
    "match_limit": 1,
}


def create_run(schema: dict, exclude_list: list | None = None) -> str:
    payload = {**schema}
    if exclude_list:
        payload["exclude_list"] = exclude_list
    response = requests.post(f"{BASE_URL}/findall/runs", json=payload, headers=HEADERS)
    response.raise_for_status()
    return response.json()["findall_id"]


def pull_status(run_id: str) -> dict:
    response = requests.get(f"{BASE_URL}/findall/runs/{run_id}", headers=HEADERS)
    response.raise_for_status()
    print(response.json())
    return response.json()


def wait_for_completion(run_id: str, poll_interval: int = 5) -> dict:
    while True:
        result = pull_status(run_id)
        status = result["status"]["status"]
        print(f"Status: {status}")
        if status in ["completed", "failed", "cancelled"]:
            return result
        time.sleep(poll_interval)


def get_results(run_id: str) -> dict:
    response = requests.get(f"{BASE_URL}/findall/runs/{run_id}/result", headers=HEADERS)
    print(response.json())
    response.raise_for_status()
    return response.json()


def get_matched_candidates(run_id: str) -> list[dict]:
    results = get_results(run_id)
    return [
        {"name": x["name"], "url": x["url"]}
        for x in results["candidates"]
        if x["match_status"] == "matched"
    ]


def save_matched_candidates(run_id: str, output_file: Path = Path("matched.json")):
    candidates = get_matched_candidates(run_id)
    output_file.write_text(json.dumps(candidates, indent=2))
    print(f"Saved {len(candidates)} matched candidates to {output_file}")


def get_schema(run_id: str) -> dict:
    response = requests.get(f"{BASE_URL}/findall/runs/{run_id}/schema", headers=HEADERS)
    response.raise_for_status()
    return response.json()


def save_results(run_id: str, output_file: Path):
    results = get_results(run_id)
    output_file.write_text(json.dumps(results, indent=4))


def build_exclude_list(run_id: str) -> list[dict]:
    results = get_results(run_id)
    return [
        {"name": c["name"], "url": c["url"]}
        for c in results.get("matched_candidates", [])
    ]


def run(exclude_from: str | None = None, save_to: str | None = None):
    exclude_list = build_exclude_list(exclude_from) if exclude_from else None
    findall_id = create_run(SCHEMA, exclude_list)
    print(f"Created run: {findall_id}")
    result = wait_for_completion(findall_id)
    if save_to:
        save_results(findall_id, Path(save_to))
    return result


def main():
    app = typer.Typer()
    app.command()(run)
    app.command()(pull_status)
    app.command()(wait_for_completion)
    app.command()(get_results)
    app.command()(get_schema)
    app.command()(save_results)
    app.command()(build_exclude_list)
    app.command()(get_matched_candidates)
    app.command()(save_matched_candidates)
    app()


if __name__ == "__main__":
    main()
