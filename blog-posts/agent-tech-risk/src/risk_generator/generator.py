"""Generate risk cases using Claude Agent SDK."""
import asyncio
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

from risk_generator.models import CompanyProfile, PROFILE_PRESETS
from risk_generator.categories import RISK_CATEGORIES, get_category

load_dotenv()

# Bedrock configuration
BEDROCK_MODEL = "us.anthropic.claude-sonnet-4-20250514-v1:0"
BEDROCK_REGION = "us-east-2"
USE_BEDROCK = bool(os.getenv("AWS_BEARER_TOKEN_BEDROCK"))


PROMPT_TEMPLATE = """
Generate a realistic AWS infrastructure state for PE due diligence.

## Company Profile
{profile}

## Risk Categories to Inject
{risk_descriptions}

## Instructions
Create realistic AWS resources that would exist in a company of this size.
Include the specified risks but make them look organic - things that happen 
in real companies, not obviously broken. Each risk should have a plausible 
business reason for existing.

Write exactly these 4 files (use these exact filenames, no directory prefix):

1. **aws_state.json** - Full AWS state snapshot with this structure:
```json
{{
  "iam": {{
    "roles": [...],
    "policies": [...],
    "users": [...]
  }},
  "s3": {{
    "buckets": [...]
  }},
  "ec2": {{
    "instances": [...],
    "security_groups": [...],
    "vpcs": [...]
  }},
  "rds": {{
    "instances": [...]
  }},
  "lambda": {{
    "functions": [...]
  }},
  "eks": {{
    "clusters": [...],
    "node_groups": [...]
  }}
}}
```

2. **risks.yaml** - Ground truth labels:
```yaml
- category: tr1
  resource: arn:aws:iam::123456789:policy/example
  issue: "Description of the issue"
  severity: critical|high|medium|low
  why: "Business reason this exists"
```

3. **narrative.md** - Business context explaining:
- Company background
- How they grew
- Why these issues accumulated
- Team structure and constraints

4. **diagram.md** - Mermaid flowchart:
- Use flowchart TB (top to bottom)
- Group resources in subgraphs (VPC, IAM, S3, etc.)
- Mark risky resources with :::risk class
- Add classDef risk fill:#ff6b6b,stroke:#c92a2a,color:#fff
- Include a table at the bottom listing all risks

Make it realistic for a {size} company with {engineers} engineers.

IMPORTANT: Write files as "aws_state.json", "risks.yaml", "narrative.md", "diagram.md" (no path prefix).
"""


def build_prompt(profile: CompanyProfile, risk_codes: list[str]) -> str:
    """Build the generation prompt."""
    size_map = {"small": "50", "medium": "150", "large": "300+"}
    engineers = size_map[profile.size]

    risk_descriptions = []
    for code in risk_codes:
        cat = get_category(code)
        risk_descriptions.append(
            f"- **{code}: {cat.name}** - {cat.description}\n"
            f"  Examples: {', '.join(cat.example_issues[:2])}"
        )

    profile_str = (
        f"- Name: {profile.name}\n"
        f"- Domain: {profile.domain}\n"
        f"- Size: {profile.size} ({engineers} engineers)\n"
        f"- AWS Accounts: {profile.aws_accounts}\n"
        f"- Has Kubernetes: {profile.has_kubernetes}"
    )

    return PROMPT_TEMPLATE.format(
        profile=profile_str,
        risk_descriptions="\n".join(risk_descriptions),
        size=profile.size,
        engineers=engineers,
    )


async def generate_case_async(
    profile: CompanyProfile | str,
    risk_codes: list[str],
    output_dir: Path,
) -> dict:
    """Generate a risk case using Claude Agent SDK."""
    from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, AssistantMessage, ToolUseBlock

    # Resolve profile
    if isinstance(profile, str):
        if profile not in PROFILE_PRESETS:
            raise ValueError(f"Unknown profile: {profile}")
        profile = PROFILE_PRESETS[profile]

    # Validate risks
    for code in risk_codes:
        if code not in RISK_CATEGORIES:
            raise ValueError(f"Unknown risk: {code}")

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save profile metadata
    with open(output_dir / "profile.yaml", "w") as f:
        yaml.dump({
            "name": profile.name,
            "domain": profile.domain,
            "size": profile.size,
            "aws_accounts": profile.aws_accounts,
            "has_kubernetes": profile.has_kubernetes,
            "risk_categories": risk_codes,
        }, f, default_flow_style=False)

    # Configure SDK options
    options_kwargs = {
        "allowed_tools": ["Write"],
        "cwd": str(output_dir),
        "permission_mode": "bypassPermissions",
        "max_turns": 20,
    }
    
    if USE_BEDROCK:
        os.environ["CLAUDE_CODE_USE_BEDROCK"] = "1"
        os.environ["AWS_REGION"] = BEDROCK_REGION
        options_kwargs["model"] = BEDROCK_MODEL
        print(f"[bedrock] model={BEDROCK_MODEL}, region={BEDROCK_REGION}")

    # Track stats
    stats = {"files_written": [], "cost": None, "tokens": None, "duration_ms": None}

    async for message in query(prompt=build_prompt(profile, risk_codes), options=ClaudeAgentOptions(**options_kwargs)):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock) and block.name == "Write":
                    path = block.input.get("file_path", "")
                    stats["files_written"].append(path)
                    print(f"[write] {path}")
        
        if isinstance(message, ResultMessage):
            stats["cost"] = message.total_cost_usd
            stats["tokens"] = message.usage
            stats["duration_ms"] = message.duration_ms
            if message.is_error:
                print(f"[error] {message.result}")
    
    return stats


def generate_case_sync(
    profile: CompanyProfile | str,
    risk_codes: list[str],
    output_dir: Path,
) -> dict:
    """Sync wrapper for generate_case_async."""
    return asyncio.run(generate_case_async(profile, risk_codes, output_dir))
