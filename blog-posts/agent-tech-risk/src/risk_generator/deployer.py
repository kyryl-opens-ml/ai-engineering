import json
from pathlib import Path

import boto3
from botocore.config import Config
from rich.console import Console

LOCALSTACK_ENDPOINT = "http://localhost:4566"
REGION = "us-east-1"

console = Console()


def get_client(service: str):
    return boto3.client(
        service,
        endpoint_url=LOCALSTACK_ENDPOINT,
        region_name=REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(retries={"max_attempts": 2}),
    )


def safe_get(d: dict, *keys, default=None):
    for key in keys:
        if key in d:
            return d[key]
    return default


def deploy_case(case_dir: Path) -> dict:
    state_file = case_dir / "aws_state.json"
    if not state_file.exists():
        raise FileNotFoundError(f"aws_state.json not found in {case_dir}")

    with open(state_file) as f:
        state = json.load(f)

    results = {"deployed": [], "failed": [], "skipped": []}

    if "iam" in state:
        deploy_iam_resources(state["iam"], results)

    if "s3" in state:
        deploy_s3_resources(state["s3"], results)

    if "ec2" in state:
        deploy_ec2_resources(state["ec2"], results)

    if "rds" in state:
        deploy_rds_resources(state["rds"], results)

    if "lambda" in state:
        deploy_lambda_resources(state["lambda"], results)

    return results


def deploy_iam_resources(iam_state: dict, results: dict):
    iam = get_client("iam")

    for policy in iam_state.get("policies", []):
        name = safe_get(policy, "name", "policy_name")
        doc = safe_get(policy, "document", "policy_document", default={})
        if not name:
            continue
        try:
            iam.create_policy(PolicyName=name, PolicyDocument=json.dumps(doc))
            results["deployed"].append(f"iam:policy:{name}")
        except Exception as e:
            results["failed"].append(f"iam:policy:{name} - {e}")

    for role in iam_state.get("roles", []):
        name = safe_get(role, "name", "role_name")
        assume = safe_get(role, "assume_policy", "assume_role_policy", default={})
        if not name:
            continue
        try:
            iam.create_role(RoleName=name, AssumeRolePolicyDocument=json.dumps(assume))
            results["deployed"].append(f"iam:role:{name}")
        except Exception as e:
            results["failed"].append(f"iam:role:{name} - {e}")

    for user in iam_state.get("users", []):
        name = safe_get(user, "name", "user_name")
        if not name:
            continue
        try:
            iam.create_user(UserName=name)
            results["deployed"].append(f"iam:user:{name}")
        except Exception as e:
            results["failed"].append(f"iam:user:{name} - {e}")


def deploy_s3_resources(s3_state: dict, results: dict):
    s3 = get_client("s3")

    for bucket in s3_state.get("buckets", []):
        name = safe_get(bucket, "name", "bucket_name")
        if not name:
            continue
        try:
            s3.create_bucket(Bucket=name)
            results["deployed"].append(f"s3:bucket:{name}")
        except Exception as e:
            results["failed"].append(f"s3:bucket:{name} - {e}")


def deploy_ec2_resources(ec2_state: dict, results: dict):
    ec2 = get_client("ec2")

    for vpc in ec2_state.get("vpcs", []):
        cidr = safe_get(vpc, "cidr", "cidr_block", default="10.0.0.0/16")
        try:
            resp = ec2.create_vpc(CidrBlock=cidr)
            vpc_id = resp["Vpc"]["VpcId"]
            results["deployed"].append(f"ec2:vpc:{vpc_id}")
        except Exception as e:
            results["failed"].append(f"ec2:vpc - {e}")

    for sg in ec2_state.get("security_groups", []):
        name = safe_get(sg, "name", "group_name")
        desc = safe_get(sg, "description", default="")
        if not name:
            continue
        try:
            resp = ec2.create_security_group(GroupName=name, Description=desc)
            sg_id = resp["GroupId"]
            results["deployed"].append(f"ec2:sg:{name}")
        except Exception as e:
            results["failed"].append(f"ec2:sg:{name} - {e}")


def deploy_rds_resources(rds_state: dict, results: dict):
    rds = get_client("rds")

    for db in rds_state.get("instances", []):
        db_id = safe_get(db, "identifier", "db_instance_identifier")
        if not db_id:
            continue
        try:
            rds.create_db_instance(
                DBInstanceIdentifier=db_id,
                DBInstanceClass=safe_get(db, "instance_class", "db_instance_class", default="db.t3.micro"),
                Engine=safe_get(db, "engine", default="postgres"),
                MasterUsername="admin",
                MasterUserPassword="localstack123",
                AllocatedStorage=20,
            )
            results["deployed"].append(f"rds:db:{db_id}")
        except Exception as e:
            results["failed"].append(f"rds:db:{db_id} - {e}")


def deploy_lambda_resources(lambda_state: dict, results: dict):
    lam = get_client("lambda")

    for func in lambda_state.get("functions", []):
        name = safe_get(func, "name", "function_name")
        if not name:
            continue
        try:
            lam.create_function(
                FunctionName=name,
                Runtime=safe_get(func, "runtime", default="python3.9"),
                Role="arn:aws:iam::000000000000:role/lambda-role",
                Handler=safe_get(func, "handler", default="index.handler"),
                Code={"ZipFile": b"# placeholder"},
            )
            results["deployed"].append(f"lambda:function:{name}")
        except Exception as e:
            results["failed"].append(f"lambda:function:{name} - {e}")


def reset_localstack():
    import subprocess
    subprocess.run(["docker", "compose", "down", "-v"], capture_output=True)
    subprocess.run(["docker", "compose", "up", "-d"], capture_output=True)


def verify_deployment() -> dict:
    counts = {}

    try:
        iam = get_client("iam")
        counts["iam_roles"] = len(iam.list_roles()["Roles"])
        counts["iam_policies"] = len(iam.list_policies(Scope="Local")["Policies"])
    except Exception:
        counts["iam_roles"] = 0
        counts["iam_policies"] = 0

    try:
        s3 = get_client("s3")
        counts["s3_buckets"] = len(s3.list_buckets()["Buckets"])
    except Exception:
        counts["s3_buckets"] = 0

    try:
        ec2 = get_client("ec2")
        counts["ec2_vpcs"] = len(ec2.describe_vpcs()["Vpcs"])
        counts["ec2_sgs"] = len(ec2.describe_security_groups()["SecurityGroups"])
    except Exception:
        counts["ec2_vpcs"] = 0
        counts["ec2_sgs"] = 0

    return counts
