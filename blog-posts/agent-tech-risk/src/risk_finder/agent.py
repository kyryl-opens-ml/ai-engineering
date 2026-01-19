import json
import os
from typing import Optional

import boto3
from pydantic_ai import Agent

from risk_finder.models import ScanResult

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


_risk_agent: Optional[Agent[None, ScanResult]] = None


def get_risk_agent() -> Agent[None, ScanResult]:
    global _risk_agent
    if _risk_agent is None:
        _risk_agent = Agent(
            "anthropic:claude-sonnet-4-20250514",
            output_type=ScanResult,
            system_prompt=SYSTEM_PROMPT,
        )
        _risk_agent.tool_plain(execute_boto3)
    return _risk_agent


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


def scan_aws() -> ScanResult:
    agent = get_risk_agent()
    result = agent.run_sync("Scan this AWS environment for technical risks and report all findings.")
    return result.output
