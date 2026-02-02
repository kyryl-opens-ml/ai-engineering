from pathlib import Path
from typing import Callable

import yaml
from pydantic_evals import Case, Dataset

from risk_finder.models import ExpectedRisk, ScanResult
from risk_finder.eval.evaluators import CategoryRecallEvaluator, RiskCountEvaluator
from risk_finder.eval.runner import run_case_in_container


def load_risks_yaml(risks_file: Path) -> list[ExpectedRisk]:
    if not risks_file.exists():
        return []

    with open(risks_file) as f:
        data = yaml.safe_load(f)

    if not data:
        return []

    risks = []
    for item in data:
        risks.append(ExpectedRisk(
            category=item.get("category", ""),
            resource=item.get("resource", ""),
            issue=item.get("issue", ""),
            severity=item.get("severity", "medium"),
        ))
    return risks


def build_dataset(cases_dir: Path) -> Dataset[dict, ScanResult, None]:
    cases = []

    for case_path in sorted(cases_dir.iterdir()):
        if not case_path.is_dir():
            continue

        if not (case_path / "aws_state.json").exists():
            continue

        expected = load_risks_yaml(case_path / "risks.yaml")

        cases.append(Case(
            name=case_path.name,
            inputs={"case_path": str(case_path)},
            expected_output=expected,
        ))

    return Dataset(
        name="risk_finder_eval",
        cases=cases,
        evaluators=[
            CategoryRecallEvaluator(),
            RiskCountEvaluator(),
        ],
    )


def create_scan_task(model: str) -> Callable[[dict], ScanResult]:
    def scan_task(inputs: dict) -> ScanResult:
        case_path = Path(inputs["case_path"])
        return run_case_in_container(case_path, model)
    return scan_task
