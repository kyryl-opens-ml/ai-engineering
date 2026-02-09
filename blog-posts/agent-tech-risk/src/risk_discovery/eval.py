"""Evaluation - run risk discovery against HF dataset cases."""

import json
import subprocess
import time

import yaml
from rich.console import Console
from rich.table import Table

from risk_discovery.agent import discover_risks
from risk_discovery.models import RiskFinding
from risk_generator.deployer import (
    deploy_resources,
    find_free_port,
    start_localstack,
    wait_for_localstack,
)

console = Console()

MODELS = {
    "opus-4-6": "bedrock:us.anthropic.claude-opus-4-6-v1",
    "opus-4-5": "bedrock:us.anthropic.claude-opus-4-5-20251101-v1:0",
    "sonnet-4-5": "bedrock:us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    "haiku-4-5": "bedrock:us.anthropic.claude-haiku-4-5-20251001-v1:0",
}

HF_DATASET = "koml/agent-tech-risk-cases"


def load_cases() -> list[dict]:
    """Load cases from HF dataset."""
    from huggingface_hub import hf_hub_download

    path = hf_hub_download(HF_DATASET, "dataset.jsonl", repo_type="dataset")
    cases = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            risks_raw = row["risks"]
            # risks stored as YAML string
            risks = yaml.safe_load(risks_raw) if isinstance(risks_raw, str) else risks_raw
            if isinstance(risks, dict) and "risks" in risks:
                risks = risks["risks"]
            # filter skipped
            risks = [r for r in (risks or []) if r.get("_status", "active") != "skipped"]

            cases.append({
                "name": row["case_id"],
                "aws_state": json.loads(row["aws_state"]) if isinstance(row["aws_state"], str) else row["aws_state"],
                "risks": risks,
            })
    return cases


def _token_overlap(a: str, b: str) -> float:
    """Token overlap ratio between two strings."""
    tokens_a = set(a.replace("-", " ").replace("_", " ").lower().split())
    tokens_b = set(b.replace("-", " ").replace("_", " ").lower().split())
    if not tokens_a or not tokens_b:
        return 0.0
    return len(tokens_a & tokens_b) / min(len(tokens_a), len(tokens_b))


def _resource_match(gt_resource: str, f_resource: str) -> bool:
    """Check if two resource names refer to the same resource."""
    a = gt_resource.lower()
    b = f_resource.lower()
    return a in b or b in a or _token_overlap(a, b) >= 0.5


def match_risks(findings: list[RiskFinding], ground_truth: list[dict]) -> dict:
    """Match agent findings against ground truth risks.

    Two-pass matching:
      1. Strict: same category + resource name overlap
      2. Relaxed: resource name overlap only (agent may use a different but valid category)
    """
    matched_gt: set[int] = set()
    matched_f: set[int] = set()

    # Pass 1: strict category + resource
    for i, gt in enumerate(ground_truth):
        gt_cat = gt["category"]
        gt_resource = gt.get("resource", "")
        for j, f in enumerate(findings):
            if j in matched_f:
                continue
            if f.category == gt_cat and _resource_match(gt_resource, f.resource):
                matched_gt.add(i)
                matched_f.add(j)
                break

    # Pass 2: resource-only for remaining unmatched GT risks
    for i, gt in enumerate(ground_truth):
        if i in matched_gt:
            continue
        gt_resource = gt.get("resource", "")
        for j, f in enumerate(findings):
            if j in matched_f:
                continue
            if _resource_match(gt_resource, f.resource):
                matched_gt.add(i)
                matched_f.add(j)
                break

    tp = len(matched_gt)
    fp = len(findings) - len(matched_f)
    fn = len(ground_truth) - len(matched_gt)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
    }


def _deploy_case(case: dict) -> dict:
    """Deploy a single case to a Docker LocalStack container."""
    port = find_free_port()
    container_id = start_localstack(port)
    endpoint = f"http://localhost:{port}"

    if not wait_for_localstack(port):
        subprocess.run(["docker", "rm", "-f", container_id], capture_output=True)
        raise RuntimeError(f"LocalStack failed for {case['name']}")

    r = deploy_resources(case["aws_state"], endpoint)
    console.print(
        f"  [dim]{case['name']}: {len(r['deployed'])} resources deployed[/dim]"
    )

    return {"port": port, "container_id": container_id, "endpoint": endpoint}


def evaluate_model(
    model_name: str,
    model_id: str,
    cases: list[dict],
    deployments: list[dict],
) -> dict:
    """Evaluate a single model across all deployed cases."""
    results = []

    for case, dep in zip(cases, deployments):
        console.print(f"  {case['name']}...", end=" ")
        try:
            start = time.time()
            scan = discover_risks(model_id, dep["endpoint"])
            elapsed = time.time() - start

            metrics = match_risks(scan.findings, case["risks"])
            metrics["case"] = case["name"]
            metrics["time"] = elapsed
            metrics["found"] = len(scan.findings)
            metrics["expected"] = len(case["risks"])
            results.append(metrics)

            console.print(
                f"P={metrics['precision']:.0%} R={metrics['recall']:.0%} "
                f"F1={metrics['f1']:.0%} ({elapsed:.0f}s)"
            )
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            results.append({"case": case["name"], "error": str(e)})

    errors = sum(1 for r in results if "error" in r)
    return {
        "model": model_name,
        "cases": results,
        "errors": errors,
        "avg_precision": _avg(results, "precision"),
        "avg_recall": _avg(results, "recall"),
        "avg_f1": _avg(results, "f1"),
        "avg_time": _avg(results, "time"),
    }


def _avg(results: list[dict], key: str) -> float:
    """Average across all cases. Errors count as 0 (not excluded)."""
    return sum(r.get(key, 0) for r in results) / len(results) if results else 0


def run_eval(
    models: dict[str, str] | None = None,
    max_cases: int | None = None,
) -> list[dict]:
    """Run full evaluation: deploy cases once, then test each model."""
    if models is None:
        models = MODELS

    # Load
    console.print("[bold]Loading cases from HuggingFace...[/bold]")
    cases = load_cases()
    if max_cases:
        cases = cases[:max_cases]
    console.print(f"Loaded {len(cases)} cases\n")

    # Deploy all cases once
    console.print("[bold]Deploying cases to LocalStack...[/bold]")
    deployments = []
    for case in cases:
        try:
            dep = _deploy_case(case)
            deployments.append(dep)
        except Exception as e:
            console.print(f"  [red]{case['name']}: {e}[/red]")
            deployments.append(None)

    # Filter out failed deployments
    valid = [(c, d) for c, d in zip(cases, deployments) if d is not None]
    if not valid:
        console.print("[red]No cases deployed successfully[/red]")
        return []
    valid_cases, valid_deps = zip(*valid)
    valid_cases, valid_deps = list(valid_cases), list(valid_deps)
    console.print(f"\n{len(valid_cases)} cases ready\n")

    # Evaluate each model
    all_results = []
    for name, model_id in models.items():
        console.print(f"\n[bold]Model: {name}[/bold] ({model_id})")
        result = evaluate_model(name, model_id, valid_cases, valid_deps)
        all_results.append(result)

    # Cleanup containers
    console.print("\n[dim]Cleaning up containers...[/dim]")
    for dep in valid_deps:
        subprocess.run(
            ["docker", "rm", "-f", dep["container_id"]], capture_output=True
        )

    # Summary table
    print_comparison(all_results)

    return all_results


def print_comparison(all_results: list[dict]):
    """Print the final comparison table."""
    table = Table(title="Model Comparison")
    table.add_column("Model", style="bold")
    table.add_column("Precision", justify="right")
    table.add_column("Recall", justify="right")
    table.add_column("F1", justify="right")
    table.add_column("Errors", justify="right")
    table.add_column("Avg Time", justify="right")

    for r in all_results:
        f1 = r["avg_f1"]
        style = "green" if f1 >= 0.6 else "yellow" if f1 >= 0.3 else "red"
        errors = r.get("errors", 0)
        err_style = "red" if errors > 0 else "green"
        table.add_row(
            r["model"],
            f"{r['avg_precision']:.1%}",
            f"{r['avg_recall']:.1%}",
            f"[{style}]{f1:.1%}[/{style}]",
            f"[{err_style}]{errors}[/{err_style}]",
            f"{r['avg_time']:.0f}s",
        )

    console.print("\n")
    console.print(table)
