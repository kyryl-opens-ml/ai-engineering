import json
import os

import boto3
from braintrust.otel import BraintrustSpanProcessor
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from pydantic_ai import Agent

from risk_finder.models import ScanResult

load_dotenv()

if not os.getenv("BRAINTRUST_PROJECT"):
    os.environ["BRAINTRUST_PROJECT"] = "risk-finder"

provider = TracerProvider()
trace.set_tracer_provider(provider)
provider.add_span_processor(BraintrustSpanProcessor())
Agent.instrument_all()

SYSTEM_PROMPT = """You are an AWS security analyst performing technical due diligence.
Your task is to scan the AWS environment and identify technical risks.

Use the execute_boto3 tool to query AWS services. The code you write should:
1. Use boto3 to query AWS resources
2. Assign the result to a variable called `output`

Start by discovering what resources exist:
1. List S3 buckets and check their configurations (encryption, public access, versioning)
2. List IAM roles and policies, check for wildcards (*) in actions/resources
3. List security groups and check for 0.0.0.0/0 ingress rules
4. List RDS instances and check multi_az, backup_retention, encryption
5. Check for any other misconfigurations you find

Risk categories to look for:
- tr1: IAM Overprivilege (wildcard permissions, cross-account trust with *)
- tr3: Storage Misconfiguration (public buckets, unencrypted storage)
- tr4: Network Exposure (open security groups, public databases)
- tr7: Single Points of Failure (single-AZ databases, no redundancy)
- tr9: Low SLA (no backups, no DR)
- tr14: Observability Gaps (no CloudTrail, no alarms)

After gathering information, return a structured ScanResult with all findings."""


def execute_boto3(code: str) -> str:
    """Execute boto3 code against AWS. Assign result to `output` variable.

    Example: output = boto3.client('s3').list_buckets()['Buckets']

    Args:
        code: Python code using boto3. Must assign result to `output`.
    """
    endpoint_url = os.environ.get("AWS_ENDPOINT_URL", "http://localhost:4566")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")

    def get_client(service: str):
        return boto3.client(
            service,
            endpoint_url=endpoint_url,
            region_name=region,
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "test"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "test"),
        )

    local_vars = {
        "boto3": boto3,
        "json": json,
        "os": os,
        "get_client": get_client,
    }

    safe_builtins = {
        "str": str,
        "list": list,
        "dict": dict,
        "len": len,
        "int": int,
        "float": float,
        "bool": bool,
        "True": True,
        "False": False,
        "None": None,
        "print": print,
        "range": range,
        "enumerate": enumerate,
        "zip": zip,
        "sorted": sorted,
        "isinstance": isinstance,
        "type": type,
    }

    try:
        exec(code, {"__builtins__": safe_builtins}, local_vars)
        output = local_vars.get("output")
        return json.dumps(output, default=str, indent=2)
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"


def create_risk_agent(model: str = "anthropic:claude-sonnet-4-20250514") -> Agent[None, ScanResult]:
    agent = Agent(
        model,
        output_type=ScanResult,
        system_prompt=SYSTEM_PROMPT,
    )
    agent.tool_plain(execute_boto3)
    return agent


def scan_aws(model: str = "anthropic:claude-sonnet-4-20250514") -> ScanResult:
    agent = create_risk_agent(model)
    result = agent.run_sync("Scan this AWS environment for technical risks and report all findings.")
    return result.output
