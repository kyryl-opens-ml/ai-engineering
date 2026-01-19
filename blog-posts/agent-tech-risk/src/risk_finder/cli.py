from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

app = typer.Typer(help="AWS Risk Finder - Detect technical risks in AWS infrastructure")
console = Console()


@app.command()
def scan():
    """Scan the current AWS environment for technical risks.
    
    Uses AWS_ENDPOINT_URL environment variable for LocalStack.
    """
    from risk_finder.agent import scan_aws

    console.print("[blue]Scanning AWS environment for technical risks...[/blue]")

    try:
        result = scan_aws()

        console.print(f"\n[green]Scan complete![/green]")
        console.print(f"Resources scanned: {result.resources_scanned}")
        console.print(f"Findings: {len(result.findings)}\n")

        if result.findings:
            table = Table(title="Risk Findings")
            table.add_column("Severity", style="bold")
            table.add_column("Category")
            table.add_column("Resource")
            table.add_column("Title")

            for finding in result.findings:
                severity_style = {
                    "critical": "bold red",
                    "high": "bold orange3",
                    "medium": "bold yellow",
                    "low": "dim",
                }.get(finding.severity, "white")

                table.add_row(
                    f"[{severity_style}]{finding.severity.upper()}[/{severity_style}]",
                    finding.category,
                    finding.resource_arn[:50] + "..." if len(finding.resource_arn) > 50 else finding.resource_arn,
                    finding.title,
                )

            console.print(table)
        else:
            console.print("[green]No technical risks found.[/green]")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command("eval")
def evaluate(
    cases: Path = typer.Option("./cases", "--cases", "-c", help="Path to cases directory"),
    max_concurrency: int = typer.Option(1, "--concurrency", "-n", help="Max concurrent evaluations"),
):
    """Evaluate the risk finder agent against test cases.
    
    Each case is run in an isolated LocalStack container.
    """
    from risk_finder.eval.dataset import build_dataset, scan_task

    if not cases.exists():
        console.print(f"[red]Cases directory not found: {cases}[/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Building evaluation dataset from {cases}...[/blue]")

    dataset = build_dataset(cases)
    console.print(f"Found {len(dataset.cases)} cases\n")

    if not dataset.cases:
        console.print("[yellow]No valid cases found.[/yellow]")
        raise typer.Exit(0)

    console.print("[blue]Running evaluation (this may take a while)...[/blue]\n")

    try:
        report = dataset.evaluate_sync(
            task=scan_task,
            name="risk_finder",
            max_concurrency=max_concurrency,
            progress=True,
        )

        report.print()

    except Exception as e:
        console.print(f"[red]Evaluation error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def run_case(
    case_path: Path = typer.Argument(..., help="Path to a single case directory"),
):
    """Run risk finder on a single case with isolated LocalStack."""
    from risk_finder.eval.runner import run_case_in_container

    if not case_path.exists():
        console.print(f"[red]Case not found: {case_path}[/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Running case: {case_path.name}[/blue]")
    console.print("[dim]Starting LocalStack container...[/dim]")

    try:
        result = run_case_in_container(case_path)

        console.print(f"\n[green]Case complete![/green]")
        console.print(f"Resources scanned: {result.resources_scanned}")
        console.print(f"Findings: {len(result.findings)}\n")

        for finding in result.findings:
            severity_style = {
                "critical": "bold red",
                "high": "bold orange3",
                "medium": "bold yellow",
                "low": "dim",
            }.get(finding.severity, "white")

            console.print(f"[{severity_style}][{finding.severity.upper()}][/{severity_style}] {finding.category}: {finding.title}")
            console.print(f"  Resource: {finding.resource_arn}")
            console.print(f"  {finding.description}\n")

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
