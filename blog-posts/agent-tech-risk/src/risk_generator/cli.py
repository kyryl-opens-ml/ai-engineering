"""Risk Generator CLI - generate, deploy, create, batch, export-hf, config."""
import json
import random
from pathlib import Path

import typer
import yaml
from rich.console import Console
from rich.table import Table

from risk_generator.categories import RISK_CATEGORIES, LOCALSTACK_FREE_CATEGORIES, list_categories
from risk_generator.models import PROFILE_PRESETS
from risk_generator.generator import generate_case_sync
from risk_generator.deployer import deploy_to_localstack

app = typer.Typer(help="AWS Risk Case Generator for PE Due Diligence")
console = Console()


# 10 curated case plans for diverse PE scenarios
CASE_PLANS = [
    {
        "profile": "payflow",
        "risks": ["tr1", "tr4"],
        "label": "Fintech startup — IAM debt + network exposure from rapid growth",
    },
    {
        "profile": "cloudsync",
        "risks": ["tr1", "tr3", "tr14"],
        "label": "SaaS platform — overprivileged roles, public storage, no monitoring",
    },
    {
        "profile": "meddata",
        "risks": ["tr1", "tr2", "tr4"],
        "label": "Healthcare company — secrets exposure + compliance violations",
    },
    {
        "profile": "shipfast",
        "risks": ["tr3", "tr4", "tr15"],
        "label": "E-commerce — public storage, open ports, orphaned resources",
    },
    {
        "profile": "devpipe",
        "risks": ["tr1", "tr2", "tr13"],
        "label": "DevTools — admin keys, EOL runtimes, exposed secrets",
    },
    {
        "profile": "insurenet",
        "risks": ["tr1", "tr4", "tr5"],
        "label": "Insurance — cross-account sprawl + network misconfig",
    },
    {
        "profile": "datavault",
        "risks": ["tr2", "tr3", "tr9"],
        "label": "Data platform — unencrypted storage, no backup strategy",
    },
    {
        "profile": "quickcart",
        "risks": ["tr1", "tr4", "tr8", "tr15"],
        "label": "Large marketplace — capacity issues + accumulated tech debt",
    },
    {
        "profile": "healthbridge",
        "risks": ["tr1", "tr2", "tr3"],
        "label": "Telehealth — HIPAA-relevant storage + secrets issues",
    },
    {
        "profile": "codeforge",
        "risks": ["tr1", "tr13", "tr15"],
        "label": "Dev platform — outdated infrastructure, poor resource hygiene",
    },
]


@app.command()
def generate(
    profile: str = typer.Option("cloudsync", "--profile", "-p", help="Company profile"),
    risks: str = typer.Option(..., "--risks", "-r", help="Risk categories (e.g., tr1,tr4)"),
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
        console.print(f"[green]Generated at {output_path}[/green]")
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

        console.print(f"[green]Deployed {result['deployed_count']} resources[/green]")
        for r in result["deployed"][:10]:
            console.print(f"  [green]+[/green] {r}")
        if result["deployed_count"] > 10:
            console.print(f"  ... and {result['deployed_count'] - 10} more")

        if result["skipped"]:
            console.print(f"[dim]Skipped {len(result['skipped'])} resources (Pro required)[/dim]")

        if result["failed"]:
            console.print(f"[yellow]Failed {len(result['failed'])}[/yellow]")
            for r in result["failed"]:
                console.print(f"  [yellow]-[/yellow] {r}")

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
    output: str = typer.Option(None, "--output", "-o", help="Output directory (auto if not set)"),
):
    """Generate a case and validate deployment."""
    # Defaults
    if profile is None:
        profile = random.choice(list(PROFILE_PRESETS.keys()))

    if risks is None:
        risk_codes = random.sample(LOCALSTACK_FREE_CATEGORIES, random.randint(2, 4))
    else:
        risk_codes = [r.strip() for r in risks.split(",")]
        non_free = [r for r in risk_codes if r not in LOCALSTACK_FREE_CATEGORIES]
        if non_free:
            console.print(f"[yellow]Note: {non_free} need LocalStack Pro for full deployment[/yellow]")

    if output is None:
        import time
        output = f"cases/case_{int(time.time())}"

    output_path = Path(output)

    # Step 1: Generate
    console.print(f"\n[bold]Step 1: Generate[/bold]")
    console.print(f"  Profile: {profile}, Risks: {risk_codes}")

    try:
        generate_case_sync(profile, risk_codes, output_path)
        console.print(f"[green]Generated at {output_path}[/green]")
    except Exception as e:
        console.print(f"[red]Generation failed: {e}[/red]")
        raise typer.Exit(1)

    # Step 2: Deploy (to validate and update risks.yaml)
    console.print(f"\n[bold]Step 2: Validate & Update Risks[/bold]")

    try:
        result = deploy_to_localstack(output_path, keep_running=False)
        console.print(f"[green]Validated {result['deployed_count']} resources[/green]")

        if result["skipped"]:
            console.print(f"[dim]Skipped {len(result['skipped'])} (Pro required)[/dim]")

        if result.get("risks"):
            r = result["risks"]
            console.print(f"[green]Risks updated: {r['active_count']}/{r['original_count']} active[/green]")

        console.print(f"\n[bold]Case ready at: {output_path}[/bold]")
    except Exception as e:
        console.print(f"[red]Validation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def batch(
    count: int = typer.Option(10, "--count", "-n", help="Number of cases to generate"),
    output: str = typer.Option("cases", "--output", "-o", help="Base output directory"),
    validate: bool = typer.Option(False, "--validate", "-v", help="Deploy each case to LocalStack to validate"),
):
    """Generate multiple cases using predefined plans."""
    plans = CASE_PLANS[:count]
    base_path = Path(output)

    table = Table(title=f"Generating {len(plans)} cases")
    table.add_column("#", style="dim")
    table.add_column("Profile")
    table.add_column("Risks")
    table.add_column("Description")

    for i, plan in enumerate(plans, 1):
        table.add_row(str(i), plan["profile"], ", ".join(plan["risks"]), plan["label"])
    console.print(table)

    results = []
    for i, plan in enumerate(plans, 1):
        case_dir = base_path / f"case_{plan['profile']}"
        console.print(f"\n[bold]--- Case {i}/{len(plans)}: {plan['profile']} ---[/bold]")
        console.print(f"  Risks: {plan['risks']}")
        console.print(f"  Output: {case_dir}")

        try:
            stats = generate_case_sync(plan["profile"], plan["risks"], case_dir)
            console.print(f"  [green]Generated[/green]")

            if validate:
                try:
                    deploy_result = deploy_to_localstack(case_dir, keep_running=False)
                    console.print(f"  [green]Validated: {deploy_result['deployed_count']} deployed[/green]")
                    results.append({"case": plan["profile"], "status": "ok", "deployed": deploy_result["deployed_count"]})
                except Exception as e:
                    console.print(f"  [yellow]Validation failed: {e}[/yellow]")
                    results.append({"case": plan["profile"], "status": "gen_ok_validate_fail", "error": str(e)})
            else:
                results.append({"case": plan["profile"], "status": "ok"})
        except Exception as e:
            console.print(f"  [red]Failed: {e}[/red]")
            results.append({"case": plan["profile"], "status": "failed", "error": str(e)})

    # Summary
    console.print(f"\n[bold]Summary[/bold]")
    ok = sum(1 for r in results if r["status"] == "ok")
    console.print(f"  Generated: {ok}/{len(plans)}")
    failed = [r for r in results if r["status"] == "failed"]
    if failed:
        console.print(f"  [red]Failed: {len(failed)}[/red]")
        for r in failed:
            console.print(f"    - {r['case']}: {r.get('error', 'unknown')}")


@app.command(name="export-hf")
def export_hf(
    cases_dir: str = typer.Argument("cases", help="Directory containing case subdirectories"),
    output: str = typer.Option("dataset.jsonl", "--output", "-o", help="Output JSONL file"),
):
    """Export cases as HuggingFace-compatible JSONL dataset."""
    cases_path = Path(cases_dir)
    if not cases_path.exists():
        console.print(f"[red]Directory not found: {cases_dir}[/red]")
        raise typer.Exit(1)

    records = []
    for case_dir in sorted(cases_path.iterdir()):
        if not case_dir.is_dir() or not (case_dir / "aws_state.json").exists():
            continue

        record = {"case_id": case_dir.name}

        # Profile — flat scalar fields, safe for Arrow
        profile_file = case_dir / "profile.yaml"
        if profile_file.exists():
            p = yaml.safe_load(profile_file.read_text())
            record["company_name"] = p.get("name", "")
            record["domain"] = p.get("domain", "")
            record["size"] = p.get("size", "")
            record["aws_accounts"] = p.get("aws_accounts", 0)
            record["has_kubernetes"] = p.get("has_kubernetes", False)
            record["risk_categories"] = ",".join(p.get("risk_categories", []))

        # Complex nested structures stored as JSON strings to avoid Arrow type conflicts
        state_file = case_dir / "aws_state.json"
        if state_file.exists():
            record["aws_state"] = state_file.read_text()

        risks_file = case_dir / "risks.yaml"
        if risks_file.exists():
            record["risks"] = risks_file.read_text()

        narrative_file = case_dir / "narrative.md"
        if narrative_file.exists():
            record["narrative"] = narrative_file.read_text()

        diagram_file = case_dir / "diagram.md"
        if diagram_file.exists():
            record["diagram"] = diagram_file.read_text()

        records.append(record)

    output_path = Path(output)
    with open(output_path, "w") as f:
        for record in records:
            f.write(json.dumps(record, default=str) + "\n")

    console.print(f"[green]Exported {len(records)} cases to {output_path}[/green]")
    console.print(f"Load with: datasets.load_dataset('json', data_files='{output_path}')")


@app.command()
def config():
    """Show current configuration."""
    import os
    from risk_generator.generator import USE_BEDROCK, BEDROCK_MODEL, BEDROCK_REGION

    console.print("[bold]Configuration[/bold]\n")

    # Bedrock status
    if USE_BEDROCK:
        console.print("[green]Bedrock enabled[/green]")
        console.print(f"  Model: {BEDROCK_MODEL}")
        console.print(f"  Region: {BEDROCK_REGION}")
        token = os.getenv("AWS_BEARER_TOKEN_BEDROCK", "")
        if token:
            console.print(f"  Token: {token[:20]}...{token[-10:]}")
    else:
        console.print("[yellow]Using Anthropic API[/yellow]")

    # Profiles
    console.print(f"\n[bold]Profiles[/bold] ({len(PROFILE_PRESETS)} available)")
    table = Table()
    table.add_column("Key")
    table.add_column("Name")
    table.add_column("Domain")
    table.add_column("Size")
    table.add_column("K8s")
    for key, p in PROFILE_PRESETS.items():
        table.add_row(key, p.name, p.domain, p.size, "yes" if p.has_kubernetes else "no")
    console.print(table)

    # Risk categories
    console.print(f"\n[bold]Risk Categories[/bold] ({len(RISK_CATEGORIES)} total, {len(LOCALSTACK_FREE_CATEGORIES)} free-tier)")
    table = Table()
    table.add_column("Code")
    table.add_column("Name")
    table.add_column("Free Tier")
    for code, cat in RISK_CATEGORIES.items():
        free = "[green]yes[/green]" if cat.localstack_free else "[dim]Pro[/dim]"
        table.add_row(code, cat.name, free)
    console.print(table)


def main():
    app()


if __name__ == "__main__":
    main()
