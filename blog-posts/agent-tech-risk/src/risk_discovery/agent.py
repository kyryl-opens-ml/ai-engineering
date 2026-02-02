"""Risk discovery agent using Pydantic AI."""
import json
import os

import boto3
from dotenv import load_dotenv
from pydantic_ai import Agent
from pydantic_ai.models.anthropic import AnthropicModel

from risk_discovery.models import ScanResult

load_dotenv()

# Check if Bedrock is available
USE_BEDROCK = bool(os.getenv("AWS_BEARER_TOKEN_BEDROCK"))
BEDROCK_REGION = "us-east-2"

SYSTEM_PROMPT = """You are an AWS security analyst performing technical due diligence.
Scan the AWS environment and identify technical risks.

Use the execute_boto3 tool to query AWS services. The code must:
1. Use get_client(service_name) to get a boto3 client
2. Assign the result to a variable called `output`

Steps:
1. List S3 buckets - check encryption, public access, versioning
2. List IAM roles/policies - check for wildcards (*) in actions/resources
3. List security groups - check for 0.0.0.0/0 ingress
4. List RDS instances - check multi_az, backup_retention, encryption
5. List Lambda functions - check runtime versions

Risk categories:
- tr1: IAM Overprivilege (wildcards, cross-account trust)
- tr3: Storage Misconfiguration (public buckets, no encryption)
- tr4: Network Exposure (open security groups)
- tr7: Single Points of Failure (single-AZ)
- tr13: Outdated Stack (old runtimes)

Return a structured ScanResult with all findings."""


def create_boto3_tool(endpoint_url: str):
    """Create a boto3 execution tool for the given endpoint."""
    
    def execute_boto3(code: str) -> str:
        """Execute boto3 code against AWS. Use get_client(service) and assign result to `output`.
        
        Example: output = get_client('s3').list_buckets()['Buckets']
        """
        def get_client(service: str):
            return boto3.client(
                service,
                endpoint_url=endpoint_url,
                region_name="us-east-1",
                aws_access_key_id="test",
                aws_secret_access_key="test",
            )
        
        local_vars = {"get_client": get_client, "json": json}
        safe_builtins = {
            "str": str, "list": list, "dict": dict, "len": len,
            "int": int, "bool": bool, "True": True, "False": False,
            "None": None, "print": print, "range": range,
            "enumerate": enumerate, "sorted": sorted,
        }
        
        try:
            exec(code, {"__builtins__": safe_builtins}, local_vars)
            output = local_vars.get("output")
            return json.dumps(output, default=str, indent=2)
        except Exception as e:
            return f"Error: {type(e).__name__}: {e}"
    
    return execute_boto3


def get_model(model_name: str):
    """Get the appropriate model, using Bedrock if available."""
    if USE_BEDROCK and not model_name.startswith("bedrock:"):
        # Convert anthropic model to bedrock format
        os.environ["AWS_REGION"] = BEDROCK_REGION
        return f"bedrock:us.anthropic.claude-sonnet-4-20250514-v1:0"
    return model_name


def scan_aws(model: str, endpoint_url: str) -> ScanResult:
    """Scan AWS environment at the given endpoint for risks."""
    actual_model = get_model(model)
    print(f"[agent] Using model: {actual_model}")
    
    agent = Agent(
        actual_model,
        output_type=ScanResult,
        system_prompt=SYSTEM_PROMPT,
    )
    agent.tool_plain(create_boto3_tool(endpoint_url))
    
    result = agent.run_sync("Scan this AWS environment for technical risks.")
    return result.output
