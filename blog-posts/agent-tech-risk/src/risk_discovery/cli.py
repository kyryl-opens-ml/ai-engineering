"""Risk Discovery CLI - Find technical risks in AWS infrastructure."""
from pathlib import Path

import yaml
import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

app = typer.Typer(help="AWS Risk Discovery - Detect technical risks")
console = Console()

DEFAULT_MODEL = "anthropic:claude-sonnet-4-20250514"


def load_ground_truth(case_path: Path) -> list[dict]:
    """Load expected risks from risks.yaml."""
    risks_file = case_path / "risks.yaml"
    if not risks_file.exists():
        return []
    
    data = yaml.safe_load(risks_file.read_text())
    if isinstance(data, dict) and "risks" in data:
        return [r for r in data["risks"] if r.get("_status") != "skipped"]
    elif isinstance(data, list):
        return data
    return []


def calculate_metrics(findings: list, ground_truth: list) -> dict:
    """Calculate recall and precision by category."""
    # Group ground truth by category
    expected_by_cat = {}
    for r in ground_truth:
        cat = r.get("category", "")
        expected_by_cat[cat] = expected_by_cat.get(cat, 0) + 1
    
    # Group findings by category
    found_by_cat = {}
    for f in findings:
        cat = f.category
        found_by_cat[cat] = found_by_cat.get(cat, 0) + 1
    
    # Calculate matches (category-level)
    all_categories = set(expected_by_cat.keys()) | set(found_by_cat.keys())
    
    true_positives = 0
    for cat in all_categories:
        expected = expected_by_cat.get(cat, 0)
        found = found_by_cat.get(cat, 0)
        true_positives += min(expected, found)
    
    total_expected = sum(expected_by_cat.values())
    total_found = len(findings)
    
    recall = true_positives / total_expected if total_expected > 0 else 0
    precision = true_positives / total_found if total_found > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        "expected": total_expected,
        "found": total_found,
        "matched": true_positives,
        "recall": recall,
        "precision": precision,
        "f1": f1,
        "expected_by_cat": expected_by_cat,
        "found_by_cat": found_by_cat,
    }


@app.command()
def run(
    case: Path = typer.Argument(..., help="Path to case directory"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="LLM model"),
    keep: bool = typer.Option(False, "--keep", "-k", help="Keep LocalStack running"),
):
    """Run risk discovery on a case."""
    from risk_discovery.agent import scan_aws
    from risk_generator.deployer import deploy_to_localstack
    
    if not case.exists():
        console.print(f"[red]Case not found: {case}[/red]")
        raise typer.Exit(1)
    
    console.print(f"[bold]Case: {case}[/bold]")
    console.print(f"[bold]Model: {model}[/bold]\n")
    
    # Step 1: Deploy to LocalStack
    console.print("[blue]Step 1: Deploy to LocalStack[/blue]")
    try:
        deploy_result = deploy_to_localstack(case, keep_running=True)
        console.print(f"[green]✓ Deployed {deploy_result['deployed_count']} resources[/green]")
        endpoint = deploy_result["endpoint"]
        container_id = deploy_result["container_id"]
    except Exception as e:
        console.print(f"[red]Deploy failed: {e}[/red]")
        raise typer.Exit(1)
    
    # Step 2: Run agent
    console.print(f"\n[blue]Step 2: Scan for risks[/blue]")
    try:
        result = scan_aws(model, endpoint)
        console.print(f"[green]✓ Scan complete[/green]")
        console.print(f"  Resources scanned: {result.resources_scanned}")
        console.print(f"  Findings: {len(result.findings)}")
    except Exception as e:
        console.print(f"[red]Scan failed: {e}[/red]")
        # Cleanup
        import subprocess
        subprocess.run(["docker", "rm", "-f", container_id], capture_output=True)
        raise typer.Exit(1)
    
    # Step 3: Show findings
    if result.findings:
        console.print(f"\n[bold]Findings:[/bold]")
        table = Table()
        table.add_column("Severity", style="bold")
        table.add_column("Category")
        table.add_column("Resource")
        table.add_column("Issue")
        
        for f in result.findings:
            style = {"critical": "red", "high": "orange3", "medium": "yellow", "low": "dim"}.get(f.severity, "")
            table.add_row(
                f"[{style}]{f.severity.upper()}[/{style}]",
                f.category,
                f.resource_arn[:40] + "..." if len(f.resource_arn) > 40 else f.resource_arn,
                f.title,
            )
        console.print(table)
    
    # Step 4: Calculate metrics against ground truth
    ground_truth = load_ground_truth(case)
    if ground_truth:
        metrics = calculate_metrics(result.findings, ground_truth)
        
        console.print(f"\n[bold]Evaluation:[/bold]")
        console.print(f"  Expected risks: {metrics['expected']}")
        console.print(f"  Found risks: {metrics['found']}")
        console.print(f"  Matched: {metrics['matched']}")
        
        # Color-code metrics
        recall_style = "green" if metrics["recall"] >= 0.7 else "yellow" if metrics["recall"] >= 0.4 else "red"
        prec_style = "green" if metrics["precision"] >= 0.7 else "yellow" if metrics["precision"] >= 0.4 else "red"
        f1_style = "green" if metrics["f1"] >= 0.7 else "yellow" if metrics["f1"] >= 0.4 else "red"
        
        console.print(f"\n  [{recall_style}]Recall: {metrics['recall']:.1%}[/{recall_style}]")
        console.print(f"  [{prec_style}]Precision: {metrics['precision']:.1%}[/{prec_style}]")
        console.print(f"  [{f1_style}]F1 Score: {metrics['f1']:.1%}[/{f1_style}]")
        
        # Show by category
        console.print(f"\n  By Category (found/expected):")
        all_cats = set(metrics["expected_by_cat"].keys()) | set(metrics["found_by_cat"].keys())
        for cat in sorted(all_cats):
            exp = metrics["expected_by_cat"].get(cat, 0)
            fnd = metrics["found_by_cat"].get(cat, 0)
            if exp == 0:
                console.print(f"    {cat}: {fnd}/0 [dim](false positive)[/dim]")
            elif fnd == 0:
                console.print(f"    {cat}: 0/{exp} [red](missed)[/red]")
            elif fnd >= exp:
                console.print(f"    {cat}: {fnd}/{exp} [green]✓[/green]")
            else:
                console.print(f"    {cat}: {fnd}/{exp} [yellow](partial)[/yellow]")
    
    # Cleanup
    if not keep:
        import subprocess
        subprocess.run(["docker", "rm", "-f", container_id], capture_output=True)
        console.print(f"\n[dim]LocalStack stopped[/dim]")
    else:
        console.print(f"\n[yellow]LocalStack running at {endpoint}[/yellow]")
        console.print(f"[yellow]Stop with: docker rm -f {container_id}[/yellow]")


def main():
    app()


if __name__ == "__main__":
    main()
