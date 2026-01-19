import random
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from .categories import RISK_CATEGORIES, list_categories
from .models import PROFILE_PRESETS
from .generator import generate_case_sync
from .deployer import deploy_case, reset_localstack, verify_deployment

app = typer.Typer(help="AWS Risk Case Generator for PE Due Diligence")
console = Console()


@app.command()
def generate(
    profile: str = typer.Option(
        "medium_saas",
        "--profile", "-p",
        help="Company profile preset (small_fintech, medium_saas, large_healthtech)",
    ),
    risks: str = typer.Option(
        ...,
        "--risks", "-r",
        help="Comma-separated risk categories (e.g., tr1,tr7,tr13)",
    ),
    output: str = typer.Option(
        "cases/case_001",
        "--output", "-o",
        help="Output directory for generated case",
    ),
):
    """Generate a risk case using Claude Code."""
    if profile not in PROFILE_PRESETS:
        console.print(f"[red]Unknown profile: {profile}[/red]")
        console.print(f"Available: {', '.join(PROFILE_PRESETS.keys())}")
        raise typer.Exit(1)

    risk_codes = [r.strip() for r in risks.split(",")]
    for code in risk_codes:
        if code not in RISK_CATEGORIES:
            console.print(f"[red]Unknown risk category: {code}[/red]")
            console.print(f"Available: {', '.join(RISK_CATEGORIES.keys())}")
            raise typer.Exit(1)

    output_path = Path(output)
    console.print(f"[blue]Generating case with profile={profile}, risks={risk_codes}[/blue]")
    console.print(f"[blue]Output: {output_path}[/blue]")

    try:
        generate_case_sync(profile, risk_codes, output_path)
        console.print(f"[green]✓ Case generated at {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def batch(
    count: int = typer.Option(5, "--count", "-n", help="Number of cases to generate"),
    output_dir: str = typer.Option("cases", "--output", "-o", help="Base output directory"),
):
    """Generate multiple random cases."""
    profiles = list(PROFILE_PRESETS.keys())
    risk_codes = list(RISK_CATEGORIES.keys())

    for i in range(count):
        profile = random.choice(profiles)
        num_risks = random.randint(2, 4)
        risks = random.sample(risk_codes, num_risks)

        case_id = f"case_{i+1:03d}"
        output_path = Path(output_dir) / case_id

        console.print(f"\n[blue]Generating {case_id}: {profile} with {risks}[/blue]")

        try:
            generate_case_sync(profile, risks, output_path)
            console.print(f"[green]✓ {case_id} complete[/green]")
        except Exception as e:
            console.print(f"[red]✗ {case_id} failed: {e}[/red]")


@app.command()
def deploy(
    case: str = typer.Argument(..., help="Path to case directory"),
    verify: bool = typer.Option(False, "--verify", "-v", help="Verify deployment after"),
):
    """Deploy a case to LocalStack."""
    case_path = Path(case)
    if not case_path.exists():
        console.print(f"[red]Case directory not found: {case}[/red]")
        raise typer.Exit(1)

    console.print(f"[blue]Deploying {case} to LocalStack...[/blue]")

    try:
        deployed = deploy_case(case_path)
        console.print(f"[green]✓ Deployed {len(deployed)} resources[/green]")
        for resource in deployed:
            console.print(f"  - {resource}")

        if verify:
            result = verify_deployment(case_path)
            if result["match"]:
                console.print("[green]✓ Verification passed[/green]")
            else:
                console.print("[yellow]⚠ Verification mismatch[/yellow]")
                console.print(f"  Expected: {result['expected']}")
                console.print(f"  Actual: {result['actual']}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def reset():
    """Reset LocalStack (remove all resources)."""
    console.print("[yellow]Resetting LocalStack...[/yellow]")
    try:
        reset_localstack()
        console.print("[green]✓ LocalStack reset[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def categories():
    """List all risk categories."""
    table = Table(title="Risk Categories")
    table.add_column("Code", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description")
    table.add_column("AWS Resources", style="dim")

    for cat in list_categories():
        table.add_row(
            cat.code,
            cat.name,
            cat.description,
            ", ".join(cat.aws_resources[:3]),
        )

    console.print(table)


@app.command()
def profiles():
    """List available company profiles."""
    table = Table(title="Company Profiles")
    table.add_column("Preset", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Domain")
    table.add_column("Size")
    table.add_column("AWS Accounts")
    table.add_column("K8s")

    for preset, profile in PROFILE_PRESETS.items():
        table.add_row(
            preset,
            profile.name,
            profile.domain,
            profile.size,
            str(profile.aws_accounts),
            "✓" if profile.has_kubernetes else "✗",
        )

    console.print(table)


def main():
    app()


if __name__ == "__main__":
    main()
