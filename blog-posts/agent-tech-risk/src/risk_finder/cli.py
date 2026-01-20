from pathlib import Path

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

app = typer.Typer(help="AWS Risk Finder - Detect technical risks in AWS infrastructure")
console = Console()

DEFAULT_MODEL = "gateway/anthropic:claude-sonnet-4-5-20250929"

BENCHMARK_MODELS = [
    "gateway/openai:gpt-5.2-2025-12-11",
    "gateway/openai:gpt-5-mini-2025-08-07",
    "gateway/openai:gpt-5-nano-2025-08-07",
    "gateway/anthropic:claude-haiku-4-5-20251001",
    "gateway/anthropic:claude-sonnet-4-5-20250929",
    "gateway/google-vertex:gemini-3-pro-preview",
    "gateway/google-vertex:gemini-3-flash-preview",
    "gateway/groq:openai/gpt-oss-120b",
    "gateway/groq:openai/gpt-oss-20b",
]


@app.command()
def scan(
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="LLM model to use"),
):
    """Scan the current AWS environment for technical risks.

    Uses AWS_ENDPOINT_URL environment variable for LocalStack.
    """
    from risk_finder.agent import scan_aws

    console.print(f"[blue]Scanning AWS environment with {model}...[/blue]")

    try:
        result = scan_aws(model)

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
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="LLM model to use"),
):
    """Evaluate the risk finder agent against test cases.

    Each case is run in an isolated LocalStack container.
    """
    from risk_finder.eval.dataset import build_dataset, create_scan_task

    if not cases.exists():
        console.print(f"[red]Cases directory not found: {cases}[/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Building evaluation dataset from {cases}...[/blue]")
    console.print(f"[blue]Using model: {model}[/blue]")

    dataset = build_dataset(cases)
    console.print(f"Found {len(dataset.cases)} cases\n")

    if not dataset.cases:
        console.print("[yellow]No valid cases found.[/yellow]")
        raise typer.Exit(0)

    console.print("[blue]Running evaluation (this may take a while)...[/blue]\n")

    try:
        scan_task = create_scan_task(model)
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
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="LLM model to use"),
):
    """Run risk finder on a single case with isolated LocalStack."""
    from risk_finder.eval.runner import run_case_in_container

    if not case_path.exists():
        console.print(f"[red]Case not found: {case_path}[/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Running case: {case_path.name}[/blue]")
    console.print(f"[blue]Using model: {model}[/blue]")

    try:
        result = run_case_in_container(case_path, model)

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


@app.command()
def benchmark(
    cases: Path = typer.Option("./cases", "--cases", "-c", help="Path to cases directory"),
    models: list[str] = typer.Option(None, "--model", "-m", help="Models to benchmark (can specify multiple)"),
):
    """Benchmark multiple models against test cases.

    Runs evaluation for each model and compares results.
    """
    from risk_finder.eval.dataset import build_dataset, create_scan_task

    if not cases.exists():
        console.print(f"[red]Cases directory not found: {cases}[/red]")
        raise typer.Exit(1)

    models_to_test = models if models else BENCHMARK_MODELS

    console.print(f"[blue]Building evaluation dataset from {cases}...[/blue]")
    dataset = build_dataset(cases)
    console.print(f"Found {len(dataset.cases)} cases\n")

    if not dataset.cases:
        console.print("[yellow]No valid cases found.[/yellow]")
        raise typer.Exit(0)

    results = {}

    for model in models_to_test:
        console.print(f"\n[bold blue]{'='*60}[/bold blue]")
        console.print(f"[bold blue]Benchmarking: {model}[/bold blue]")
        console.print(f"[bold blue]{'='*60}[/bold blue]\n")

        try:
            scan_task = create_scan_task(model)
            report = dataset.evaluate_sync(
                task=scan_task,
                name=f"risk_finder_{model.replace('/', '_').replace(':', '_')}",
                max_concurrency=1,
                progress=True,
            )
            results[model] = report
            report.print()
        except Exception as e:
            console.print(f"[red]Error with {model}: {e}[/red]")
            results[model] = None

    console.print(f"\n[bold green]{'='*60}[/bold green]")
    console.print("[bold green]Benchmark Summary[/bold green]")
    console.print(f"[bold green]{'='*60}[/bold green]\n")

    summary_table = Table(title="Model Comparison")
    summary_table.add_column("Model", style="cyan")
    summary_table.add_column("Cases", justify="right")
    summary_table.add_column("Avg Duration", justify="right")
    summary_table.add_column("Status", style="bold")

    for model, report in results.items():
        if report is None:
            summary_table.add_row(model, "-", "-", "[red]FAILED[/red]")
        else:
            case_count = len(report.cases)
            total_duration = sum(c.task_duration for c in report.cases if c.task_duration)
            avg_duration = total_duration / case_count if case_count > 0 else 0
            summary_table.add_row(
                model,
                str(case_count),
                f"{avg_duration:.1f}s",
                "[green]OK[/green]",
            )

    console.print(summary_table)


def main():
    app()


if __name__ == "__main__":
    main()
