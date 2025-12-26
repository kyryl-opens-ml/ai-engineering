import csv
import json
import os
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import modal


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


@dataclass(frozen=True)
class QAPair:
    uid: str
    question: str
    answer: str
    difficulty: str | None = None


DEFAULT_VOLUME_NAME = "officeqa-data"
VOLUME_MOUNT = Path("/vol")
ROOT_DIR = VOLUME_MOUNT / "officeqa"
REPO_DIR = ROOT_DIR / "repo"
OFFICEQA_CSV = REPO_DIR / "officeqa.csv"

app = modal.App("databricks-officeqa-benchmark-eval-simple")

image = modal.Image.debian_slim(python_version="3.12").pip_install(
    "google-genai>=1.56.0"
)
gemini_secret = modal.Secret.from_name("gemini")
volume = modal.Volume.from_name(
    os.environ.get("OFFICEQA_VOLUME", DEFAULT_VOLUME_NAME), create_if_missing=True
)


def _load_officeqa_csv(path: Path) -> list[QAPair]:
    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows: list[QAPair] = []
        for r in reader:
            rows.append(
                QAPair(
                    uid=(r.get("uid") or "").strip(),
                    question=(r.get("question") or "").strip(),
                    answer=(r.get("answer") or "").strip(),
                    difficulty=(r.get("difficulty") or "").strip() or None,
                )
            )
    return rows


def _maybe_score_answer_fn(repo_dir: Path):
    reward_py = repo_dir / "reward.py"
    if not reward_py.exists():
        return None
    import importlib.util

    spec = importlib.util.spec_from_file_location("officeqa_reward", reward_py)
    if not spec or not spec.loader:
        return None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    fn = getattr(mod, "score_answer", None)
    return fn if callable(fn) else None


def _gemini_answer(*, client: Any, model: str, question: str) -> str:
    resp = client.models.generate_content(
        model=model,
        contents=[
            "Answer the question with a short answer only. Do not explain.",
            question,
        ],
    )
    text = getattr(resp, "text", None)
    return (text or "").strip()


def _random_baseline_answer(rng: random.Random, answers: list[str]) -> str:
    if not answers:
        return ""
    return rng.choice(answers)


@app.function(
    image=image,
    secrets=[gemini_secret],
    timeout=60 * 60 * 2,
    volumes={str(VOLUME_MOUNT): volume},
)
def eval_simple_remote(
    *,
    model: str = "gemini-2.0-flash",
    max_questions: int | None = None,
    difficulty: str | None = None,
    seed: int = 0,
    tolerance: float = 0.01,
) -> dict[str, Any]:
    from google import genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is required")
    if not OFFICEQA_CSV.exists():
        raise FileNotFoundError(str(OFFICEQA_CSV))

    qa = _load_officeqa_csv(OFFICEQA_CSV)
    if difficulty:
        qa = [x for x in qa if (x.difficulty or "").lower() == difficulty.lower()]
    if max_questions is not None:
        qa = qa[: max(0, max_questions)]

    score_answer = _maybe_score_answer_fn(REPO_DIR)
    rng = random.Random(seed)
    all_answers = [x.answer for x in qa]
    client = genai.Client(api_key=api_key)

    examples: list[dict[str, Any]] = []
    gemini_scores: list[float] = []
    rand_scores: list[float] = []

    for x in qa:
        gemini_pred = _gemini_answer(client=client, model=model, question=x.question)
        rand_pred = _random_baseline_answer(rng, all_answers)

        gemini_acc = (
            float(score_answer(x.answer, gemini_pred, tolerance=tolerance))
            if score_answer
            else float(x.answer.strip().lower() == gemini_pred.strip().lower())
        )
        rand_acc = (
            float(score_answer(x.answer, rand_pred, tolerance=tolerance))
            if score_answer
            else float(x.answer.strip().lower() == rand_pred.strip().lower())
        )

        gemini_scores.append(gemini_acc)
        rand_scores.append(rand_acc)

        examples.append(
            {
                "uid": x.uid,
                "difficulty": x.difficulty,
                "question": x.question,
                "answer": x.answer,
                "predictions": {"gemini": gemini_pred, "random": rand_pred},
                "scores": {"gemini": gemini_acc, "random": rand_acc},
            }
        )

    out = {
        "run_id": int(time.time()),
        "config": {
            "model": model,
            "max_questions": max_questions,
            "difficulty": difficulty,
            "seed": seed,
            "tolerance": tolerance,
        },
        "paths": {
            "officeqa_csv": str(OFFICEQA_CSV),
            "repo_dir": str(REPO_DIR),
        },
        "dataset": {
            "count": len(qa),
            "difficulties": sorted({x.difficulty for x in qa if x.difficulty}),
        },
        "metrics": {
            "gemini": {"accuracy": mean(gemini_scores)},
            "random": {"accuracy": mean(rand_scores)},
        },
        "examples": examples,
    }
    return out


@app.local_entrypoint()
def main(
    out_path: str = "officeqa_eval_results.json",
    model: str = "gemini-2.0-flash",
    max_questions: int | None = None,
    difficulty: str | None = None,
    seed: int = 0,
    tolerance: float = 0.01,
) -> None:
    results = eval_simple_remote.remote(
        model=model,
        max_questions=max_questions,
        difficulty=difficulty,
        seed=seed,
        tolerance=tolerance,
    )

    metrics = results["metrics"]
    print("gemini", json.dumps(metrics["gemini"], indent=2, sort_keys=True))
    print("random", json.dumps(metrics["random"], indent=2, sort_keys=True))

    Path(out_path).write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(out_path)
