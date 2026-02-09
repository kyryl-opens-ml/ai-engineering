"""Risk Discovery CLI - Find technical risks in AWS infrastructure."""

import typer
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

load_dotenv()

app = typer.Typer(help="AWS Risk Discovery - Detect technical risks")
console = Console()

DEFAULT_MODEL = "bedrock:us.anthropic.claude-sonnet-4-5-20250929-v1:0"


@app.command()
def infer(
    endpoint: str = typer.Argument(..., help="LocalStack/AWS endpoint URL"),
    model: str = typer.Option(DEFAULT_MODEL, "--model", "-m", help="Model ID"),
):
    """Discover risks on a single AWS endpoint."""
    from risk_discovery.agent import discover_risks

    console.print(f"[bold]Model:[/bold] {model}")
    console.print(f"[bold]Endpoint:[/bold] {endpoint}\n")

    result = discover_risks(model, endpoint)

    if not result.findings:
        console.print("[green]No risks found[/green]")
        return

    table = Table(title=f"{len(result.findings)} Findings")
    table.add_column("Sev", style="bold", width=8)
    table.add_column("Cat", width=5)
    table.add_column("Resource")
    table.add_column("Issue")

    for f in sorted(
        result.findings,
        key=lambda x: ["critical", "high", "medium", "low"].index(x.severity),
    ):
        style = {
            "critical": "red",
            "high": "orange3",
            "medium": "yellow",
            "low": "dim",
        }.get(f.severity, "")
        table.add_row(
            f"[{style}]{f.severity.upper()}[/{style}]",
            f.category,
            f.resource,
            f.issue[:80],
        )

    console.print(table)


@app.command(name="eval")
def eval_cmd(
    models: str = typer.Option(
        "all",
        "--models",
        "-m",
        help="Comma-separated model keys (opus-4-6,sonnet-4-5,...) or 'all'",
    ),
    max_cases: int = typer.Option(
        None, "--max-cases", "-n", help="Max cases to evaluate"
    ),
):
    """Evaluate models against HF dataset cases."""
    from risk_discovery.eval import MODELS, run_eval

    if models == "all":
        selected = MODELS
    else:
        selected = {k: MODELS[k] for k in models.split(",") if k in MODELS}
        if not selected:
            console.print(
                f"[red]No valid models. Choose from: {', '.join(MODELS)}[/red]"
            )
            raise typer.Exit(1)

    console.print(f"[bold]Models:[/bold] {', '.join(selected)}")
    if max_cases:
        console.print(f"[bold]Max cases:[/bold] {max_cases}")
    console.print()

    run_eval(models=selected, max_cases=max_cases)


def main():
    app()


if __name__ == "__main__":
    main()
