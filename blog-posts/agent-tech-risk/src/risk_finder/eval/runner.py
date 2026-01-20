import os
import time
from pathlib import Path

import boto3
import docker
from botocore.config import Config

from risk_generator.deployer import deploy_case
from risk_finder.agent import create_risk_agent
from risk_finder.models import ScanResult


def wait_for_localstack(endpoint_url: str, timeout: int = 60) -> bool:
    client = boto3.client(
        "s3",
        endpoint_url=endpoint_url,
        region_name="us-east-1",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        config=Config(retries={"max_attempts": 2}),
    )
    start = time.time()
    while time.time() - start < timeout:
        try:
            client.list_buckets()
            return True
        except Exception:
            time.sleep(1)
    return False


def run_case_in_container(case_path: Path, model: str = "anthropic:claude-sonnet-4-20250514") -> ScanResult:
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
        for _ in range(10):
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
        deploy_results = deploy_case(case_path, endpoint_url)
        print(f"  [4/5] Deployed {len(deploy_results['deployed'])} resources, {len(deploy_results['failed'])} failed")

        os.environ["AWS_ENDPOINT_URL"] = endpoint_url
        os.environ["AWS_ACCESS_KEY_ID"] = "test"
        os.environ["AWS_SECRET_ACCESS_KEY"] = "test"
        os.environ["AWS_DEFAULT_REGION"] = "us-east-1"

        print(f"  [5/5] Running AI agent ({model}) to scan for risks...")
        agent = create_risk_agent(model)
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
