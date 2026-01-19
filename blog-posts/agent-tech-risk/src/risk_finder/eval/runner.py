import json
import os
import time
from pathlib import Path

import boto3
import docker
from botocore.config import Config

from risk_finder.agent import get_risk_agent
from risk_finder.models import ScanResult


def get_client(service: str, endpoint_url: str):
    return boto3.client(
        service,
        endpoint_url=endpoint_url,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(retries={"max_attempts": 2}),
    )


def safe_get(d: dict, *keys, default=None):
    for key in keys:
        if key in d:
            return d[key]
    return default


def deploy_case_to_endpoint(case_dir: Path, endpoint_url: str) -> dict:
    state_file = case_dir / "aws_state.json"
    if not state_file.exists():
        raise FileNotFoundError(f"aws_state.json not found in {case_dir}")

    with open(state_file) as f:
        state = json.load(f)

    results = {"deployed": [], "failed": []}

    if "iam" in state:
        deploy_iam(state["iam"], endpoint_url, results)

    if "s3" in state:
        deploy_s3(state["s3"], endpoint_url, results)

    if "ec2" in state:
        deploy_ec2(state["ec2"], endpoint_url, results)

    if "rds" in state:
        deploy_rds(state["rds"], endpoint_url, results)

    if "lambda" in state:
        deploy_lambda(state["lambda"], endpoint_url, results)

    return results


def deploy_iam(iam_state: dict, endpoint_url: str, results: dict):
    iam = get_client("iam", endpoint_url)

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


def deploy_s3(s3_state: dict, endpoint_url: str, results: dict):
    s3 = get_client("s3", endpoint_url)

    for bucket in s3_state.get("buckets", []):
        name = safe_get(bucket, "name", "bucket_name")
        if not name:
            continue
        try:
            s3.create_bucket(Bucket=name)
            results["deployed"].append(f"s3:bucket:{name}")
        except Exception as e:
            results["failed"].append(f"s3:bucket:{name} - {e}")


def deploy_ec2(ec2_state: dict, endpoint_url: str, results: dict):
    ec2 = get_client("ec2", endpoint_url)

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
        desc = safe_get(sg, "description", default="Security group")
        if not name:
            continue
        try:
            ec2.create_security_group(GroupName=name, Description=desc)
            results["deployed"].append(f"ec2:sg:{name}")
        except Exception as e:
            results["failed"].append(f"ec2:sg:{name} - {e}")


def deploy_rds(rds_state: dict, endpoint_url: str, results: dict):
    rds = get_client("rds", endpoint_url)

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


def deploy_lambda(lambda_state: dict, endpoint_url: str, results: dict):
    lam = get_client("lambda", endpoint_url)

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


def wait_for_localstack(endpoint_url: str, timeout: int = 60):
    s3 = get_client("s3", endpoint_url)
    start = time.time()
    while time.time() - start < timeout:
        try:
            s3.list_buckets()
            return True
        except Exception:
            time.sleep(1)
    return False


def run_case_in_container(case_path: Path) -> ScanResult:
    print(f"  [1/5] Starting LocalStack container...")
    client = docker.from_env()

    container = client.containers.run(
        "localstack/localstack",
        detach=True,
        ports={"4566/tcp": None},
        environment={
            "SERVICES": "s3,iam,ec2,rds,lambda",
            "DEBUG": "0",
        },
    )

    try:
        print(f"  [2/5] Waiting for port binding...")
        for i in range(10):
            container.reload()
            port_bindings = container.attrs["NetworkSettings"]["Ports"].get("4566/tcp")
            if port_bindings:
                break
            time.sleep(1)
        
        if not port_bindings:
            raise RuntimeError("Could not get port binding for LocalStack")
        port = port_bindings[0]["HostPort"]
        endpoint_url = f"http://localhost:{port}"
        print(f"  [2/5] LocalStack on port {port}")

        print(f"  [3/5] Waiting for LocalStack to be ready...")
        if not wait_for_localstack(endpoint_url):
            raise RuntimeError("LocalStack did not become ready in time")
        print(f"  [3/5] LocalStack is ready!")

        print(f"  [4/5] Deploying case resources...")
        deploy_results = deploy_case_to_endpoint(case_path, endpoint_url)
        print(f"  [4/5] Deployed {len(deploy_results['deployed'])} resources, {len(deploy_results['failed'])} failed")

        os.environ["AWS_ENDPOINT_URL"] = endpoint_url
        os.environ["AWS_ACCESS_KEY_ID"] = "test"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

        print(f"  [5/5] Running AI agent to scan for risks...")
        agent = get_risk_agent()
        result = agent.run_sync("Scan this AWS environment for technical risks and report all findings.")
        print(f"  [5/5] Agent finished! Found {len(result.output.findings)} risks")
        return result.output

    finally:
        print(f"  Cleaning up container...")
        try:
            container.stop()
            container.remove()
        except Exception:
            pass
