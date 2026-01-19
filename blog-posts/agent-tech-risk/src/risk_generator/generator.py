import asyncio
from pathlib import Path

import yaml
from dotenv import load_dotenv

from risk_generator.models import CompanyProfile, PROFILE_PRESETS
from risk_generator.categories import RISK_CATEGORIES, get_category

load_dotenv()


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

Write these files in the current directory:

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
"""


def build_prompt(profile: CompanyProfile, risk_codes: list[str]) -> str:
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
) -> None:
    from claude_agent_sdk import query, ClaudeAgentOptions

    if isinstance(profile, str):
        if profile not in PROFILE_PRESETS:
            raise ValueError(f"Unknown profile preset: {profile}")
        profile = PROFILE_PRESETS[profile]

    for code in risk_codes:
        if code not in RISK_CATEGORIES:
            raise ValueError(f"Unknown risk category: {code}")

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    profile_data = {
        "name": profile.name,
        "domain": profile.domain,
        "size": profile.size,
        "aws_accounts": profile.aws_accounts,
        "has_kubernetes": profile.has_kubernetes,
        "risk_categories": risk_codes,
    }
    with open(output_dir / "profile.yaml", "w") as f:
        yaml.dump(profile_data, f, default_flow_style=False)

    prompt = build_prompt(profile, risk_codes)

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            allowed_tools=["Write"],
            cwd=str(output_dir),
            permission_mode="bypassPermissions",
        ),
    ):
        if hasattr(message, "result"):
            print(message.result)
        elif hasattr(message, "content"):
            print(message.content)


def generate_case_sync(
    profile: CompanyProfile | str,
    risk_codes: list[str],
    output_dir: Path,
) -> None:
    asyncio.run(generate_case_async(profile, risk_codes, output_dir))
