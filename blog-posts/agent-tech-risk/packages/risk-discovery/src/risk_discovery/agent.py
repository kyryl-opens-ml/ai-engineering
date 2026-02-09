"""Risk discovery agent using Pydantic AI."""

import json
import os
from dataclasses import dataclass

import boto3
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from risk_discovery.models import ScanResult

load_dotenv()

os.environ.setdefault("AWS_REGION", "us-east-2")

SYSTEM_PROMPT = """\
You are an AWS security analyst performing technical due diligence for a PE acquisition.
Scan the AWS environment thoroughly and identify ALL technical risks.

Use the execute_boto3 tool to query AWS services. Write Python code that:
1. Calls get_client(service_name) to get a boto3 client
2. Assigns the final result to a variable called `output`

Scan ALL of these services systematically:

1. IAM - list_policies(Scope='Local'), list_roles(), list_users(). For each policy,
   get_policy_version to read the document. Check for:
   - Wildcard (*) in Action or Resource
   - Cross-account trust with Principal: * or AWS: *
   - Overprivileged policies attached to roles/users

2. S3 - list_buckets(). For each bucket check:
   - get_public_access_block (disabled = risk)
   - get_bucket_versioning (not Enabled = risk)
   - No encryption configured

3. EC2 - describe_security_groups(). Check for:
   - Ingress from 0.0.0.0/0 on sensitive ports (22, 3306, 5432, 6379, 27017)
   - All ports open (FromPort=0, ToPort=65535)
   - Overly permissive rules

4. Lambda - list_functions(). For each function check:
   - Outdated runtimes (python3.8, python3.7, nodejs14.x, nodejs12.x)
   - Secrets/credentials in environment variables (look for PASSWORD, KEY, SECRET, TOKEN)
   - Under-provisioned memory (128MB)

5. DynamoDB - list_tables(), describe_table(). Check for:
   - No SSE encryption (SSEDescription missing or not enabled)
   - No point-in-time recovery (describe_continuous_backups)

6. SecretsManager - list_secrets(). Check for:
   - No rotation configured (RotationEnabled=false)

7. SQS - list_queues(), get_queue_attributes(). Check for:
   - No encryption
   - No dead letter queue (RedrivePolicy missing)

Risk categories:
- tr1: IAM Overprivilege (wildcards, cross-account trust, admin policies)
- tr2: Secrets Exposure (plaintext credentials in env vars, no rotation)
- tr3: Storage Misconfiguration (public buckets, no encryption, no versioning)
- tr4: Network Exposure (open security groups, 0.0.0.0/0 ingress)
- tr5: Multi-Account Sprawl (cross-account trust issues)
- tr8: Capacity Gaps (under-provisioned Lambda, wrong instance types)
- tr9: Low SLA (no backups, no DR, no PITR)
- tr13: Outdated Stack (EOL runtimes)
- tr14: Observability Gaps (no alarms, no logging)
- tr15: Resource Hygiene (orphaned resources, missing tags)

Be thorough. Scan every service. Report every issue as a separate finding.
Use the exact resource name (policy name, bucket name, sg name, function name) in each finding."""


@dataclass
class Deps:
    endpoint_url: str


agent = Agent(
    "bedrock:us.anthropic.claude-sonnet-4-5-20250929-v1:0",
    deps_type=Deps,
    output_type=ScanResult,
    system_prompt=SYSTEM_PROMPT,
)


@agent.tool
def execute_boto3(ctx: RunContext[Deps], code: str) -> str:
    """Execute boto3 code against AWS. Use get_client(service) to get a client.
    Assign result to `output`.

    Example: output = get_client('s3').list_buckets()['Buckets']
    """

    def get_client(service: str):
        return boto3.client(
            service,
            endpoint_url=ctx.deps.endpoint_url,
            region_name="us-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

    local_vars = {"get_client": get_client, "json": json}
    safe_builtins = {
        "str": str,
        "list": list,
        "dict": dict,
        "len": len,
        "int": int,
        "bool": bool,
        "True": True,
        "False": False,
        "None": None,
        "print": print,
        "range": range,
        "enumerate": enumerate,
        "sorted": sorted,
        "isinstance": isinstance,
        "set": set,
        "tuple": tuple,
        "zip": zip,
        "map": map,
        "filter": filter,
        "any": any,
        "all": all,
        "min": min,
        "max": max,
        "sum": sum,
        "type": type,
        "hasattr": hasattr,
        "getattr": getattr,
    }

    try:
        exec(code, {"__builtins__": safe_builtins}, local_vars)
        output = local_vars.get("output")
        return json.dumps(output, default=str, indent=2)
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


def discover_risks(model: str, endpoint_url: str) -> ScanResult:
    """Run the agent to discover risks at the given endpoint."""
    result = agent.run_sync(
        "Scan this AWS environment for all technical risks. Be thorough - check every service.",
        model=model,
        deps=Deps(endpoint_url=endpoint_url),
    )
    return result.output
