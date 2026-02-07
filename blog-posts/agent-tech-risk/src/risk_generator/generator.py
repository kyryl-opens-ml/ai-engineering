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


PROMPT_TEMPLATE = """You are generating a realistic AWS infrastructure audit case for PE (private equity) due diligence.

## Company Profile
{profile}

## Risk Categories to Inject
{risk_descriptions}

## Context
This case targets PE deal teams, technical architects, and asset managers evaluating acquisition targets.
Risks must feel organic — accumulated through growth, urgency, team changes, and competing priorities.
Every risk needs a believable business story explaining why it exists.

## Instructions

Write exactly 4 files (use exact filenames, no directory prefix):

### 1. aws_state.json

Use ONLY these LocalStack free-tier services with EXACT PascalCase field names:

```json
{{
  "iam": {{
    "roles": [{{
      "RoleName": "string",
      "AssumeRolePolicyDocument": {{"Version": "2012-10-17", "Statement": [...]}},
      "AttachedPolicies": ["PolicyName1"]
    }}],
    "policies": [{{
      "PolicyName": "string",
      "PolicyDocument": {{"Version": "2012-10-17", "Statement": [...]}}
    }}],
    "users": [{{
      "UserName": "string",
      "AttachedPolicies": ["PolicyName1"]
    }}]
  }},
  "s3": {{
    "buckets": [{{
      "Name": "string",
      "Versioning": "Enabled|Suspended",
      "Encryption": "AES256|SSE-S3|None",
      "PublicAccessBlock": {{
        "BlockPublicAcls": true,
        "IgnorePublicAcls": true,
        "BlockPublicPolicy": true,
        "RestrictPublicBuckets": true
      }}
    }}]
  }},
  "ec2": {{
    "instances": [{{
      "InstanceId": "i-xxxx",
      "InstanceType": "t3.large",
      "State": "running",
      "Tags": {{"Name": "string", "Environment": "production"}}
    }}],
    "security_groups": [{{
      "GroupName": "string",
      "Description": "string",
      "IngressRules": [{{
        "IpProtocol": "tcp",
        "FromPort": 443,
        "ToPort": 443,
        "CidrBlocks": ["0.0.0.0/0"]
      }}]
    }}],
    "vpcs": [{{
      "CidrBlock": "10.0.0.0/16",
      "Tags": {{"Name": "string"}}
    }}]
  }},
  "lambda": {{
    "functions": [{{
      "FunctionName": "string",
      "Runtime": "python3.9|python3.11|nodejs18.x|nodejs20.x",
      "Handler": "index.handler",
      "MemorySize": 256,
      "Timeout": 30,
      "Role": "arn:aws:iam::123456789012:role/RoleName",
      "Environment": {{"KEY": "value"}}
    }}]
  }},
  "dynamodb": {{
    "tables": [{{
      "TableName": "string",
      "KeySchema": [{{"AttributeName": "id", "KeyType": "HASH"}}],
      "AttributeDefinitions": [{{"AttributeName": "id", "AttributeType": "S"}}],
      "BillingMode": "PAY_PER_REQUEST",
      "SSESpecification": {{"Enabled": false}},
      "PointInTimeRecoveryEnabled": false,
      "Tags": {{"Environment": "production"}}
    }}]
  }},
  "secretsmanager": {{
    "secrets": [{{
      "Name": "string",
      "SecretString": "plaintext-value-or-json",
      "Tags": {{"Environment": "production"}}
    }}]
  }},
  "sqs": {{
    "queues": [{{
      "QueueName": "string",
      "Attributes": {{"VisibilityTimeout": "30"}}
    }}]
  }}
}}
```

**Rules:**
- Do NOT include rds, eks, elasticache, ecs, or cloudfront sections
- Use DynamoDB tables instead of RDS for database resources
- For secrets exposure: put credentials in Lambda Environment vars AND/OR SecretsManager
- For network risks: use security group IngressRules with 0.0.0.0/0 on sensitive ports
- Resource count by company size: small=10-20, medium=20-30, large=35-50
- Realistic ratio: ~70% properly configured resources, ~30% with issues
- Use realistic naming: company prefix, environment tags, descriptive names
- AttachedPolicies in roles/users must reference PolicyName values from the policies list

### 2. risks.yaml

Ground truth labels:

```yaml
- category: tr1
  resource: "Exact PolicyName, GroupName, FunctionName, etc. from aws_state.json"
  issue: "Specific description of what is wrong"
  severity: critical|high|medium|low
  why: "Business story — growth pressure, team changes, acquisitions, deadlines"
```

Requirements:
- Include {min_risks}-{max_risks} risks total across all requested categories
- Each risk's "resource" field must exactly match a resource name in aws_state.json
- Severity mix: 1-2 critical, 2-4 high, 1-3 medium, 0-1 low
- The "why" should be a specific mini-story (not generic)

### 3. narrative.md

A compelling due diligence narrative covering:
- Company background, founding year, what they build, who they sell to
- Growth timeline with concrete milestones (revenue, headcount, customers, funding rounds)
- Specific decisions and events that created technical debt
- Current engineering team structure (size, security team, infra team)
- Why each risk category exists — tied to specific business events
- What a PE buyer would need to remediate post-acquisition

Write for PE deal teams who evaluate dozens of companies. Make it specific and memorable.

### 4. diagram.md

Mermaid flowchart of the infrastructure:
- Use `flowchart TB`
- Group resources in subgraphs (VPC, IAM, Storage, Compute, Data, etc.)
- Mark risky resources with `:::risk`
- Add `classDef risk fill:#ff6b6b,stroke:#c92a2a,color:#fff`
- Include risk summary table at bottom
- Keep it readable — focus on key resources and relationships

IMPORTANT: Write files as "aws_state.json", "risks.yaml", "narrative.md", "diagram.md" — no path prefix.
Make it realistic for a {size} company with {engineers} engineers."""


def build_prompt(profile: CompanyProfile, risk_codes: list[str]) -> str:
    """Build the generation prompt."""
    size_map = {"small": "50", "medium": "150", "large": "300+"}
    risk_range = {"small": (5, 8), "medium": (7, 12), "large": (10, 15)}
    engineers = size_map[profile.size]
    min_risks, max_risks = risk_range[profile.size]

    risk_descriptions = []
    for code in risk_codes:
        cat = get_category(code)
        risk_descriptions.append(
            f"- **{code}: {cat.name}** — {cat.description}\n"
            f"  Examples: {', '.join(cat.example_issues[:3])}"
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
        min_risks=min_risks,
        max_risks=max_risks,
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
