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
LOCALSTACK_SERVICES = "iam,s3,ec2,lambda,dynamodb,secretsmanager,sqs"

# Risk categories that require LocalStack Pro
PRO_REQUIRED_CATEGORIES = {"tr6", "tr7", "tr10", "tr11", "tr12"}


def get_field(obj: dict, *keys, default=None):
    """Get field value trying multiple key names (PascalCase, snake_case, lowercase)."""
    for key in keys:
        if key in obj:
            return obj[key]
    return default


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
            "docker",
            "run",
            "-d",
            "--name",
            name,
            "-p",
            f"{port}:4566",
            "-e",
            f"SERVICES={LOCALSTACK_SERVICES}",
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

    # --- IAM ---
    if "iam" in state:
        iam = get_client("iam", endpoint)
        policy_arns = {}

        # Create policies first (so we can attach to roles/users)
        for policy in state["iam"].get("policies", []):
            name = get_field(policy, "PolicyName", "name", "policy_name")
            if not name:
                continue
            doc = get_field(policy, "PolicyDocument", "policy_document", default={})
            if not doc.get("Statement"):
                doc = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Action": "sts:GetCallerIdentity",
                            "Resource": "*",
                        }
                    ],
                }
            try:
                resp = iam.create_policy(
                    PolicyName=name, PolicyDocument=json.dumps(doc)
                )
                arn = resp["Policy"]["Arn"]
                policy_arns[name] = arn
                results["deployed"].append(f"iam:policy:{name}")
            except Exception:
                results["failed"].append(f"iam:policy:{name}")

        # Create roles and attach policies
        for role in state["iam"].get("roles", []):
            name = get_field(role, "RoleName", "name", "role_name")
            if not name:
                continue
            assume_doc = get_field(
                role,
                "AssumeRolePolicyDocument",
                "assume_role_policy_document",
                default={},
            )
            if not assume_doc.get("Version"):
                assume_doc = {"Version": "2012-10-17", "Statement": []}
            try:
                iam.create_role(
                    RoleName=name, AssumeRolePolicyDocument=json.dumps(assume_doc)
                )
                results["deployed"].append(f"iam:role:{name}")

                # Attach policies
                attached = get_field(
                    role, "AttachedPolicies", "attached_policies", default=[]
                )
                for policy_ref in attached:
                    policy_name = (
                        policy_ref.split("/")[-1]
                        if "/" in str(policy_ref)
                        else policy_ref
                    )
                    arn = policy_arns.get(policy_name)
                    if arn:
                        try:
                            iam.attach_role_policy(RoleName=name, PolicyArn=arn)
                        except Exception:
                            pass
            except Exception:
                results["failed"].append(f"iam:role:{name}")

        # Create users and attach policies
        for user in state["iam"].get("users", []):
            name = get_field(user, "UserName", "name", "user_name")
            if not name:
                continue
            try:
                iam.create_user(UserName=name)
                results["deployed"].append(f"iam:user:{name}")

                attached = get_field(
                    user, "AttachedPolicies", "attached_policies", default=[]
                )
                for policy_ref in attached:
                    policy_name = (
                        policy_ref.split("/")[-1]
                        if "/" in str(policy_ref)
                        else policy_ref
                    )
                    arn = policy_arns.get(policy_name)
                    if arn:
                        try:
                            iam.attach_user_policy(UserName=name, PolicyArn=arn)
                        except Exception:
                            pass
            except Exception:
                results["failed"].append(f"iam:user:{name}")

    # --- S3 ---
    if "s3" in state:
        s3 = get_client("s3", endpoint)
        for bucket in state["s3"].get("buckets", []):
            name = get_field(bucket, "Name", "name")
            if not name:
                continue
            try:
                s3.create_bucket(Bucket=name)
                results["deployed"].append(f"s3:bucket:{name}")

                # Public access block
                pab = get_field(bucket, "PublicAccessBlock", "public_access_block")
                if pab:
                    try:
                        s3.put_public_access_block(
                            Bucket=name,
                            PublicAccessBlockConfiguration={
                                "BlockPublicAcls": get_field(
                                    pab,
                                    "BlockPublicAcls",
                                    "block_public_acls",
                                    default=True,
                                ),
                                "IgnorePublicAcls": get_field(
                                    pab,
                                    "IgnorePublicAcls",
                                    "ignore_public_acls",
                                    default=True,
                                ),
                                "BlockPublicPolicy": get_field(
                                    pab,
                                    "BlockPublicPolicy",
                                    "block_public_policy",
                                    default=True,
                                ),
                                "RestrictPublicBuckets": get_field(
                                    pab,
                                    "RestrictPublicBuckets",
                                    "restrict_public_buckets",
                                    default=True,
                                ),
                            },
                        )
                    except Exception:
                        pass

                # Versioning
                versioning = get_field(bucket, "Versioning", "versioning")
                if versioning and str(versioning).lower() == "enabled":
                    try:
                        s3.put_bucket_versioning(
                            Bucket=name,
                            VersioningConfiguration={"Status": "Enabled"},
                        )
                    except Exception:
                        pass
            except Exception:
                results["failed"].append(f"s3:bucket:{name}")

    # --- EC2 ---
    if "ec2" in state:
        ec2 = get_client("ec2", endpoint)

        # VPCs
        for vpc in state["ec2"].get("vpcs", []):
            cidr = get_field(vpc, "CidrBlock", "cidr_block", default="10.0.0.0/16")
            try:
                resp = ec2.create_vpc(CidrBlock=cidr)
                vpc_id = resp["Vpc"]["VpcId"]
                results["deployed"].append(f"ec2:vpc:{vpc_id}")
            except Exception:
                results["failed"].append("ec2:vpc")

        # Security Groups with ingress rules
        for sg in state["ec2"].get("security_groups", []):
            name = get_field(sg, "GroupName", "group_name", "name")
            if not name:
                continue
            desc = get_field(
                sg, "Description", "description", default=f"Security group {name}"
            )
            try:
                resp = ec2.create_security_group(GroupName=name, Description=desc)
                sg_id = resp["GroupId"]
                results["deployed"].append(f"ec2:sg:{name}")

                # Deploy ingress rules
                ingress = get_field(sg, "IngressRules", "ingress_rules", default=[])
                for rule in ingress:
                    cidr_blocks = get_field(
                        rule, "CidrBlocks", "cidr_blocks", default=[]
                    )
                    from_port = get_field(rule, "FromPort", "from_port")
                    to_port = get_field(rule, "ToPort", "to_port")
                    if from_port is not None and to_port is not None and cidr_blocks:
                        try:
                            ec2.authorize_security_group_ingress(
                                GroupId=sg_id,
                                IpPermissions=[
                                    {
                                        "IpProtocol": get_field(
                                            rule,
                                            "IpProtocol",
                                            "ip_protocol",
                                            default="tcp",
                                        ),
                                        "FromPort": int(from_port),
                                        "ToPort": int(to_port),
                                        "IpRanges": [
                                            {"CidrIp": cidr} for cidr in cidr_blocks
                                        ],
                                    }
                                ],
                            )
                        except Exception:
                            pass
            except Exception:
                results["failed"].append(f"ec2:sg:{name}")

    # --- Lambda ---
    if "lambda" in state:
        lam = get_client("lambda", endpoint)
        zip_bytes = create_lambda_zip()

        for func in state["lambda"].get("functions", []):
            name = get_field(func, "FunctionName", "function_name", "name")
            if not name:
                continue
            env_vars = get_field(
                func, "Environment", "environment_variables", default={}
            )
            try:
                kwargs = {
                    "FunctionName": name,
                    "Runtime": get_field(
                        func, "Runtime", "runtime", default="python3.9"
                    ),
                    "Role": get_field(
                        func,
                        "Role",
                        "role",
                        default="arn:aws:iam::000000000000:role/lambda-role",
                    ),
                    "Handler": get_field(
                        func, "Handler", "handler", default="index.handler"
                    ),
                    "Code": {"ZipFile": zip_bytes},
                    "MemorySize": int(
                        get_field(func, "MemorySize", "memory_size", default=128)
                    ),
                    "Timeout": int(get_field(func, "Timeout", "timeout", default=30)),
                }
                if env_vars:
                    kwargs["Environment"] = {"Variables": env_vars}
                lam.create_function(**kwargs)
                results["deployed"].append(f"lambda:function:{name}")
            except Exception:
                results["failed"].append(f"lambda:function:{name}")

    # --- DynamoDB (free tier) ---
    if "dynamodb" in state:
        ddb = get_client("dynamodb", endpoint)
        for table in state["dynamodb"].get("tables", []):
            name = get_field(table, "TableName", "table_name", "name")
            if not name:
                continue
            key_schema = get_field(
                table,
                "KeySchema",
                "key_schema",
                default=[{"AttributeName": "id", "KeyType": "HASH"}],
            )
            attr_defs = get_field(
                table,
                "AttributeDefinitions",
                "attribute_definitions",
                default=[{"AttributeName": "id", "AttributeType": "S"}],
            )
            try:
                ddb.create_table(
                    TableName=name,
                    KeySchema=key_schema,
                    AttributeDefinitions=attr_defs,
                    BillingMode=get_field(
                        table, "BillingMode", "billing_mode", default="PAY_PER_REQUEST"
                    ),
                )
                results["deployed"].append(f"dynamodb:table:{name}")
            except Exception:
                results["failed"].append(f"dynamodb:table:{name}")

    # --- SecretsManager (free tier) ---
    if "secretsmanager" in state:
        sm = get_client("secretsmanager", endpoint)
        for secret in state["secretsmanager"].get("secrets", []):
            name = get_field(secret, "Name", "name")
            if not name:
                continue
            value = get_field(secret, "SecretString", "secret_string", default="{}")
            try:
                sm.create_secret(
                    Name=name,
                    SecretString=value if isinstance(value, str) else json.dumps(value),
                )
                results["deployed"].append(f"secretsmanager:secret:{name}")
            except Exception:
                results["failed"].append(f"secretsmanager:secret:{name}")

    # --- SQS (free tier) ---
    if "sqs" in state:
        sqs = get_client("sqs", endpoint)
        for queue in state["sqs"].get("queues", []):
            name = get_field(queue, "QueueName", "queue_name", "name")
            if not name:
                continue
            attrs = get_field(queue, "Attributes", "attributes", default={})
            try:
                sqs.create_queue(QueueName=name, Attributes=attrs)
                results["deployed"].append(f"sqs:queue:{name}")
            except Exception:
                results["failed"].append(f"sqs:queue:{name}")

    # --- RDS (Pro only - skip) ---
    if "rds" in state:
        for db in state["rds"].get("instances", []):
            name = get_field(
                db,
                "DBInstanceIdentifier",
                "db_instance_identifier",
                "identifier",
                "name",
            )
            if name:
                results["skipped"].append(f"rds:db:{name}")

    # --- EKS (Pro only - skip) ---
    if "eks" in state:
        for cluster in state["eks"].get("clusters", []):
            name = get_field(cluster, "name", "ClusterName")
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

    # Mark each risk as active or skipped
    active_risks = []
    skipped_risks = []

    for risk in risks:
        category = risk.get("category", "")

        # Check if this risk's category requires Pro
        is_pro_category = category in PRO_REQUIRED_CATEGORIES

        # Check if the resource was skipped
        resource = risk.get("resource", "")
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
        },
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
