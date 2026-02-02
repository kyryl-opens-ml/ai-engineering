"""Risk Generator CLI - 4 commands: generate, deploy, create, config."""
import random
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from risk_generator.categories import RISK_CATEGORIES, list_categories
from risk_generator.models import PROFILE_PRESETS
from risk_generator.generator import generate_case_sync
from risk_generator.deployer import deploy_to_localstack

app = typer.Typer(help="AWS Risk Case Generator")
console = Console()


@app.command()
def generate(
    profile: str = typer.Option("medium_saas", "--profile", "-p", help="Company profile"),
    risks: str = typer.Option(..., "--risks", "-r", help="Risk categories (e.g., tr1,tr7)"),
    output: str = typer.Option("cases/case_001", "--output", "-o", help="Output directory"),
):
    """Generate a risk case using Claude Code."""
    if profile not in PROFILE_PRESETS:
        console.print(f"[red]Unknown profile: {profile}[/red]")
        console.print(f"Available: {', '.join(PROFILE_PRESETS.keys())}")
        raise typer.Exit(1)

    risk_codes = [r.strip() for r in risks.split(",")]
    for code in risk_codes:
        if code not in RISK_CATEGORIES:
            console.print(f"[red]Unknown risk: {code}[/red]")
            raise typer.Exit(1)

    output_path = Path(output)
    console.print(f"[blue]Generating case: profile={profile}, risks={risk_codes}[/blue]")

    try:
        stats = generate_case_sync(profile, risk_codes, output_path)
        console.print(f"[green]✓ Generated at {output_path}[/green]")
        if stats.get("duration_ms"):
            console.print(f"  Duration: {stats['duration_ms'] / 1000:.1f}s")
        if stats.get("cost"):
            console.print(f"  Cost: ${stats['cost']:.4f}")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def deploy(
    case: str = typer.Argument(..., help="Path to case directory"),
    port: int = typer.Option(None, "--port", "-p", help="LocalStack port (random if not set)"),
    keep: bool = typer.Option(False, "--keep", "-k", help="Keep LocalStack running"),
):
    """Deploy a case to LocalStack."""
    case_path = Path(case)
    if not case_path.exists():
        console.print(f"[red]Case not found: {case}[/red]")
        raise typer.Exit(1)

    try:
        result = deploy_to_localstack(case_path, port=port, keep_running=keep)
        
        console.print(f"[green]✓ Deployed {result['deployed_count']} resources[/green]")
        for r in result["deployed"][:10]:
            console.print(f"  [green]✓[/green] {r}")
        if result["deployed_count"] > 10:
            console.print(f"  ... and {result['deployed_count'] - 10} more")
        
        if result["skipped"]:
            console.print(f"[dim]⊘ {len(result['skipped'])} resources skipped (Pro required)[/dim]")
        
        if result["failed"]:
            console.print(f"[yellow]⚠ {len(result['failed'])} failed[/yellow]")
        
        if result.get("risks"):
            r = result["risks"]
            console.print(f"[blue]Risks: {r['active_count']}/{r['original_count']} active[/blue]")
        
        if keep:
            console.print(f"\n[blue]Endpoint: {result['endpoint']}[/blue]")
            console.print(f"[yellow]Stop with: docker rm -f {result['container_id']}[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def create(
    profile: str = typer.Option(None, "--profile", "-p", help="Company profile (random if not set)"),
    risks: str = typer.Option(None, "--risks", "-r", help="Risk categories (random if not set)"),
    output: str = typer.Option(None, "--output", "-o", help="Output directory (auto-generated if not set)"),
):
    """Generate a case and validate deployment."""
    # Defaults
    if profile is None:
        profile = random.choice(list(PROFILE_PRESETS.keys()))
    
    # Filter to LocalStack-supported risks (exclude RDS-dependent ones)
    supported_risks = ["tr1", "tr2", "tr3", "tr4", "tr5", "tr6", "tr11", "tr12", "tr13", "tr14", "tr15"]
    
    if risks is None:
        risk_codes = random.sample(supported_risks, random.randint(2, 4))
    else:
        risk_codes = [r.strip() for r in risks.split(",")]
        unsupported = [r for r in risk_codes if r not in supported_risks]
        if unsupported:
            console.print(f"[yellow]Note: {unsupported} may not fully deploy (need LocalStack Pro)[/yellow]")
    
    if output is None:
        import time
        output = f"cases/case_{int(time.time())}"
    
    output_path = Path(output)
    
    # Step 1: Generate
    console.print(f"\n[bold]Step 1: Generate[/bold]")
    console.print(f"  Profile: {profile}, Risks: {risk_codes}")
    
    try:
        generate_case_sync(profile, risk_codes, output_path)
        console.print(f"[green]✓ Generated at {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Generation failed: {e}[/red]")
        raise typer.Exit(1)
    
    # Step 2: Deploy (to validate and update risks.yaml)
    console.print(f"\n[bold]Step 2: Validate & Update Risks[/bold]")
    
    try:
        result = deploy_to_localstack(output_path, keep_running=False)
        console.print(f"[green]✓ Validated {result['deployed_count']} resources[/green]")
        
        if result["skipped"]:
            console.print(f"[dim]⊘ {len(result['skipped'])} skipped (Pro required)[/dim]")
        
        if result.get("risks"):
            r = result["risks"]
            console.print(f"[green]✓ Risks updated: {r['active_count']}/{r['original_count']} active[/green]")
        
        console.print(f"\n[bold]Case ready at: {output_path}[/bold]")
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def config():
    """Show current configuration."""
    import os
    from risk_generator.generator import USE_BEDROCK, BEDROCK_MODEL, BEDROCK_REGION
    
    console.print("[bold]Configuration[/bold]\n")
    
    # Bedrock status
    if USE_BEDROCK:
        console.print("[green]✓ Bedrock enabled[/green]")
        console.print(f"  Model: {BEDROCK_MODEL}")
        console.print(f"  Region: {BEDROCK_REGION}")
        token = os.getenv("AWS_BEARER_TOKEN_BEDROCK", "")
        if token:
            console.print(f"  Token: {token[:20]}...{token[-10:]}")
    else:
        console.print("[yellow]⚠ Using Anthropic API[/yellow]")
    
    # Profiles
    console.print("\n[bold]Profiles[/bold]")
    for name, p in PROFILE_PRESETS.items():
        console.print(f"  {name}: {p.name} ({p.size}, {p.domain})")
    
    # Risk categories
    console.print(f"\n[bold]Risk Categories[/bold] ({len(RISK_CATEGORIES)} total)")
    for code, cat in list(RISK_CATEGORIES.items())[:5]:
        console.print(f"  {code}: {cat.name}")
    console.print("  ...")


def main():
    app()


if __name__ == "__main__":
    main()
