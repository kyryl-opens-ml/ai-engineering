import json
from pathlib import Path

import boto3
from botocore.config import Config


LOCALSTACK_ENDPOINT = "http://localhost:4566"
REGION = "us-east-1"


def get_client(service: str):
    return boto3.client(
        service,
        endpoint_url=LOCALSTACK_ENDPOINT,
        region_name=REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(retries={"max_attempts": 3}),
    )


def deploy_iam(state: dict) -> list[str]:
    deployed = []
    iam = get_client("iam")

    for policy in state.get("policies", []):
        try:
            iam.create_policy(
                PolicyName=policy["name"],
                PolicyDocument=json.dumps(policy.get("document", {})),
                Description=policy.get("description", ""),
            )
            deployed.append(f"iam:policy:{policy['name']}")
        except iam.exceptions.EntityAlreadyExistsException:
            pass

    for role in state.get("roles", []):
        try:
            iam.create_role(
                RoleName=role["name"],
                AssumeRolePolicyDocument=json.dumps(
                    role.get("assume_policy", {"Version": "2012-10-17", "Statement": []})
                ),
                Description=role.get("description", ""),
            )
            deployed.append(f"iam:role:{role['name']}")

            for policy_arn in role.get("attached_policies", []):
                iam.attach_role_policy(RoleName=role["name"], PolicyArn=policy_arn)
        except iam.exceptions.EntityAlreadyExistsException:
            pass

    for user in state.get("users", []):
        try:
            iam.create_user(UserName=user["name"])
            deployed.append(f"iam:user:{user['name']}")
        except iam.exceptions.EntityAlreadyExistsException:
            pass

    return deployed


def deploy_s3(state: dict) -> list[str]:
    deployed = []
    s3 = get_client("s3")

    for bucket in state.get("buckets", []):
        try:
            s3.create_bucket(Bucket=bucket["name"])
            deployed.append(f"s3:bucket:{bucket['name']}")

            if bucket.get("public", False):
                s3.put_public_access_block(
                    Bucket=bucket["name"],
                    PublicAccessBlockConfiguration={
                        "BlockPublicAcls": False,
                        "IgnorePublicAcls": False,
                        "BlockPublicPolicy": False,
                        "RestrictPublicBuckets": False,
                    },
                )

            if bucket.get("versioning", False):
                s3.put_bucket_versioning(
                    Bucket=bucket["name"],
                    VersioningConfiguration={"Status": "Enabled"},
                )

            if encryption := bucket.get("encryption"):
                s3.put_bucket_encryption(
                    Bucket=bucket["name"],
                    ServerSideEncryptionConfiguration={
                        "Rules": [
                            {
                                "ApplyServerSideEncryptionByDefault": {
                                    "SSEAlgorithm": encryption.get("algorithm", "AES256")
                                }
                            }
                        ]
                    },
                )
        except s3.exceptions.BucketAlreadyOwnedByYou:
            pass

    return deployed


def deploy_ec2(state: dict) -> list[str]:
    deployed = []
    ec2 = get_client("ec2")

    for vpc in state.get("vpcs", []):
        try:
            resp = ec2.create_vpc(CidrBlock=vpc.get("cidr", "10.0.0.0/16"))
            vpc_id = resp["Vpc"]["VpcId"]
            deployed.append(f"ec2:vpc:{vpc_id}")

            if tags := vpc.get("tags"):
                ec2.create_tags(
                    Resources=[vpc_id],
                    Tags=[{"Key": k, "Value": v} for k, v in tags.items()],
                )
        except Exception:
            pass

    for sg in state.get("security_groups", []):
        try:
            resp = ec2.create_security_group(
                GroupName=sg["name"],
                Description=sg.get("description", ""),
                VpcId=sg.get("vpc_id"),
            )
            sg_id = resp["GroupId"]
            deployed.append(f"ec2:security_group:{sg_id}")

            for rule in sg.get("ingress_rules", []):
                ec2.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpProtocol=rule.get("protocol", "tcp"),
                    FromPort=rule.get("from_port", 0),
                    ToPort=rule.get("to_port", 65535),
                    CidrIp=rule.get("cidr", "0.0.0.0/0"),
                )
        except ec2.exceptions.ClientError:
            pass

    return deployed


def deploy_rds(state: dict) -> list[str]:
    deployed = []
    rds = get_client("rds")

    for instance in state.get("instances", []):
        try:
            rds.create_db_instance(
                DBInstanceIdentifier=instance["identifier"],
                DBInstanceClass=instance.get("instance_class", "db.t3.micro"),
                Engine=instance.get("engine", "postgres"),
                MasterUsername=instance.get("master_username", "admin"),
                MasterUserPassword=instance.get("master_password", "password123"),
                AllocatedStorage=instance.get("allocated_storage", 20),
                MultiAZ=instance.get("multi_az", False),
                PubliclyAccessible=instance.get("publicly_accessible", False),
                BackupRetentionPeriod=instance.get("backup_retention_period", 7),
            )
            deployed.append(f"rds:instance:{instance['identifier']}")
        except rds.exceptions.DBInstanceAlreadyExistsFault:
            pass

    return deployed


def deploy_lambda(state: dict) -> list[str]:
    deployed = []
    lambda_client = get_client("lambda")

    for func in state.get("functions", []):
        try:
            lambda_client.create_function(
                FunctionName=func["name"],
                Runtime=func.get("runtime", "python3.9"),
                Role=func.get("role", "arn:aws:iam::000000000000:role/lambda-role"),
                Handler=func.get("handler", "index.handler"),
                Code={"ZipFile": b"fake-code"},
                Environment={"Variables": func.get("environment", {})},
                Timeout=func.get("timeout", 30),
                MemorySize=func.get("memory_size", 128),
            )
            deployed.append(f"lambda:function:{func['name']}")
        except lambda_client.exceptions.ResourceConflictException:
            pass

    return deployed


def deploy_case(case_dir: Path) -> list[str]:
    state_file = case_dir / "aws_state.json"
    if not state_file.exists():
        raise FileNotFoundError(f"aws_state.json not found in {case_dir}")

    with open(state_file) as f:
        state = json.load(f)

    deployed = []
    deployed.extend(deploy_iam(state.get("iam", {})))
    deployed.extend(deploy_s3(state.get("s3", {})))
    deployed.extend(deploy_ec2(state.get("ec2", {})))
    deployed.extend(deploy_rds(state.get("rds", {})))
    deployed.extend(deploy_lambda(state.get("lambda", {})))

    return deployed


def reset_localstack() -> None:
    import subprocess

    subprocess.run(
        ["docker", "compose", "down", "-v"],
        capture_output=True,
    )
    subprocess.run(
        ["docker", "compose", "up", "-d"],
        capture_output=True,
    )


def verify_deployment(case_dir: Path) -> dict:
    state_file = case_dir / "aws_state.json"
    with open(state_file) as f:
        expected = json.load(f)

    actual = {}

    iam = get_client("iam")
    try:
        roles = iam.list_roles()["Roles"]
        actual["iam_roles"] = len(roles)
    except Exception:
        actual["iam_roles"] = 0

    s3 = get_client("s3")
    try:
        buckets = s3.list_buckets()["Buckets"]
        actual["s3_buckets"] = len(buckets)
    except Exception:
        actual["s3_buckets"] = 0

    expected_counts = {
        "iam_roles": len(expected.get("iam", {}).get("roles", [])),
        "s3_buckets": len(expected.get("s3", {}).get("buckets", [])),
    }

    return {
        "expected": expected_counts,
        "actual": actual,
        "match": expected_counts == actual,
    }
