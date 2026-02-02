"""Deploy AWS state to LocalStack."""
import io
import json
import socket
import subprocess
import time
import zipfile
from pathlib import Path

import boto3
import yaml
from botocore.config import Config

REGION = "us-east-1"

# Risk categories that require LocalStack Pro (RDS, EKS, etc.)
PRO_REQUIRED_CATEGORIES = {"tr7", "tr8", "tr9", "tr10", "tr11"}


def find_free_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def start_localstack(port: int) -> str:
    """Start LocalStack container, return container ID."""
    name = f"localstack-risk-{port}"
    
    # Remove existing container if any
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)
    
    # Start container
    result = subprocess.run(
        [
            "docker", "run", "-d",
            "--name", name,
            "-p", f"{port}:4566",
            "-e", "SERVICES=iam,s3,ec2,lambda",
            "localstack/localstack",
        ],
        capture_output=True,
        text=True,
    )
    
    if result.returncode != 0:
        raise RuntimeError(f"Failed to start LocalStack: {result.stderr}")
    
    return result.stdout.strip()[:12]


def wait_for_localstack(port: int, timeout: int = 60) -> bool:
    """Wait for LocalStack to be ready."""
    import urllib.request
    
    endpoint = f"http://localhost:{port}"
    start = time.time()
    
    while time.time() - start < timeout:
        try:
            req = urllib.request.Request(f"{endpoint}/_localstack/health")
            with urllib.request.urlopen(req, timeout=2) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    
    return False


def get_client(service: str, endpoint: str):
    """Get boto3 client for LocalStack."""
    return boto3.client(
        service,
        endpoint_url=endpoint,
        region_name=REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(retries={"max_attempts": 2}),
    )


def create_lambda_zip() -> bytes:
    """Create minimal Lambda zip."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("index.py", "def handler(e,c): return {'statusCode':200}")
    buf.seek(0)
    return buf.read()


def deploy_resources(state: dict, endpoint: str) -> dict:
    """Deploy AWS resources from state to LocalStack."""
    results = {"deployed": [], "failed": [], "skipped": []}
    
    # IAM Roles
    if "iam" in state:
        iam = get_client("iam", endpoint)
        
        for role in state["iam"].get("roles", []):
            name = role.get("RoleName") or role.get("name")
            if not name:
                continue
            assume_doc = role.get("AssumeRolePolicyDocument", {})
            if not assume_doc.get("Version"):
                assume_doc = {"Version": "2012-10-17", "Statement": []}
            try:
                iam.create_role(RoleName=name, AssumeRolePolicyDocument=json.dumps(assume_doc))
                results["deployed"].append(f"iam:role:{name}")
            except Exception:
                results["failed"].append(f"iam:role:{name}")
        
        for user in state["iam"].get("users", []):
            name = user.get("UserName") or user.get("name")
            if not name:
                continue
            try:
                iam.create_user(UserName=name)
                results["deployed"].append(f"iam:user:{name}")
            except Exception:
                results["failed"].append(f"iam:user:{name}")
        
        for policy in state["iam"].get("policies", []):
            name = policy.get("PolicyName") or policy.get("name")
            if not name:
                continue
            doc = policy.get("PolicyDocument", {})
            if not doc.get("Statement"):
                doc = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": "sts:GetCallerIdentity", "Resource": "*"}]}
            try:
                iam.create_policy(PolicyName=name, PolicyDocument=json.dumps(doc))
                results["deployed"].append(f"iam:policy:{name}")
            except Exception:
                results["failed"].append(f"iam:policy:{name}")
    
    # S3 Buckets
    if "s3" in state:
        s3 = get_client("s3", endpoint)
        for bucket in state["s3"].get("buckets", []):
            name = bucket.get("Name") or bucket.get("name")
            if not name:
                continue
            try:
                s3.create_bucket(Bucket=name)
                results["deployed"].append(f"s3:bucket:{name}")
            except Exception:
                results["failed"].append(f"s3:bucket:{name}")
    
    # EC2 VPCs and Security Groups
    if "ec2" in state:
        ec2 = get_client("ec2", endpoint)
        
        for vpc in state["ec2"].get("vpcs", []):
            cidr = vpc.get("CidrBlock", "10.0.0.0/16")
            try:
                resp = ec2.create_vpc(CidrBlock=cidr)
                results["deployed"].append(f"ec2:vpc:{resp['Vpc']['VpcId']}")
            except Exception:
                results["failed"].append("ec2:vpc")
        
        for sg in state["ec2"].get("security_groups", []):
            name = sg.get("GroupName") or sg.get("name")
            if not name:
                continue
            try:
                ec2.create_security_group(GroupName=name, Description=sg.get("Description", "SG"))
                results["deployed"].append(f"ec2:sg:{name}")
            except Exception:
                results["failed"].append(f"ec2:sg:{name}")
    
    # Lambda Functions
    if "lambda" in state:
        lam = get_client("lambda", endpoint)
        zip_bytes = create_lambda_zip()
        
        for func in state["lambda"].get("functions", []):
            name = func.get("FunctionName") or func.get("name")
            if not name:
                continue
            try:
                lam.create_function(
                    FunctionName=name,
                    Runtime=func.get("Runtime", "python3.9"),
                    Role=func.get("Role", "arn:aws:iam::000000000000:role/lambda-role"),
                    Handler=func.get("Handler", "index.handler"),
                    Code={"ZipFile": zip_bytes},
                )
                results["deployed"].append(f"lambda:function:{name}")
            except Exception:
                results["failed"].append(f"lambda:function:{name}")
    
    # RDS (Pro only)
    if "rds" in state:
        for db in state["rds"].get("instances", []):
            name = db.get("DBInstanceIdentifier") or db.get("identifier")
            if name:
                results["skipped"].append(f"rds:db:{name}")
    
    # EKS (Pro only)
    if "eks" in state:
        for cluster in state["eks"].get("clusters", []):
            name = cluster.get("name")
            if name:
                results["skipped"].append(f"eks:cluster:{name}")
    
    return results


def update_risks_yaml(case_dir: Path, deployed: list[str], skipped: list[str]) -> dict:
    """Update risks.yaml to mark which risks are deployable.
    
    Returns dict with original_count, active_count, skipped_count.
    """
    risks_file = case_dir / "risks.yaml"
    if not risks_file.exists():
        return {"original_count": 0, "active_count": 0, "skipped_count": 0}
    
    content = risks_file.read_text()
    
    # Handle both formats: top-level list or dict with 'risks' key
    data = yaml.safe_load(content)
    if isinstance(data, dict) and "risks" in data:
        risks = data["risks"]
    elif isinstance(data, list):
        risks = data
    else:
        risks = []
    
    original_count = len(risks)
    
    # Build set of deployed resource identifiers
    deployed_resources = set()
    for r in deployed:
        # Extract resource name from "service:type:name" format
        parts = r.split(":")
        if len(parts) >= 3:
            deployed_resources.add(parts[2])  # Just the name
    
    # Mark each risk as active or skipped
    active_risks = []
    skipped_risks = []
    
    for risk in risks:
        category = risk.get("category", "")
        resource = risk.get("resource", "")
        
        # Check if this risk's category requires Pro
        is_pro_category = category in PRO_REQUIRED_CATEGORIES
        
        # Check if the resource was skipped
        resource_skipped = any(resource in s for s in skipped)
        
        if is_pro_category or resource_skipped:
            risk["_status"] = "skipped"
            risk["_reason"] = "LocalStack Pro required"
            skipped_risks.append(risk)
        else:
            risk["_status"] = "active"
            active_risks.append(risk)
    
    # Write updated risks.yaml
    output = {
        "risks": active_risks + skipped_risks,
        "_summary": {
            "total": original_count,
            "active": len(active_risks),
            "skipped": len(skipped_risks),
        }
    }
    
    with open(risks_file, "w") as f:
        yaml.dump(output, f, default_flow_style=False, sort_keys=False)
    
    return {
        "original_count": original_count,
        "active_count": len(active_risks),
        "skipped_count": len(skipped_risks),
    }


def deploy_to_localstack(
    case_dir: Path,
    port: int | None = None,
    keep_running: bool = False,
) -> dict:
    """Deploy case to LocalStack. Returns deployment results."""
    state_file = case_dir / "aws_state.json"
    if not state_file.exists():
        raise FileNotFoundError(f"aws_state.json not found in {case_dir}")
    
    state = json.loads(state_file.read_text())
    
    # Start LocalStack
    if port is None:
        port = find_free_port()
    
    container_id = start_localstack(port)
    endpoint = f"http://localhost:{port}"
    
    print(f"Starting LocalStack (container: {container_id}, port: {port})...")
    
    if not wait_for_localstack(port):
        subprocess.run(["docker", "rm", "-f", container_id], capture_output=True)
        raise RuntimeError("LocalStack failed to start")
    
    print(f"LocalStack ready at {endpoint}")
    
    # Deploy resources
    results = deploy_resources(state, endpoint)
    
    # Update risks.yaml with deployment status
    risks_update = update_risks_yaml(case_dir, results["deployed"], results["skipped"])
    
    # Stop if not keeping
    if not keep_running:
        subprocess.run(["docker", "rm", "-f", container_id], capture_output=True)
        print("LocalStack stopped")
    
    return {
        "endpoint": endpoint,
        "container_id": container_id,
        "deployed": results["deployed"],
        "deployed_count": len(results["deployed"]),
        "failed": results["failed"],
        "skipped": results["skipped"],
        "risks": risks_update,
    }
