#!/usr/bin/env python3
"""Deploy all risk cases to LocalStack pods in a kind cluster.

Usage:
    uv run python scripts/debug_cases.py          # create cluster + deploy all
    uv run python scripts/debug_cases.py --clean   # tear down cluster
"""
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from risk_generator.deployer import deploy_resources

CLUSTER_NAME = "risk-cases"
BASE_PORT = 14566
CASES_DIR = Path(__file__).resolve().parent.parent / "cases"
SKIP_CASES = {"case_1770000056"}


def run(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(f"FAIL: {cmd}\n{r.stderr.strip()}")
        sys.exit(1)
    return r


def create_cluster():
    existing = run("kind get clusters", check=False).stdout.strip().split()
    if CLUSTER_NAME in existing:
        print(f"Cluster '{CLUSTER_NAME}' already exists, reusing")
        run(f"kubectl config use-context kind-{CLUSTER_NAME}")
        return
    print(f"Creating kind cluster '{CLUSTER_NAME}'...")
    run(f"kind create cluster --name {CLUSTER_NAME} --wait 60s")
    print("Cluster ready")


def delete_cluster():
    print(f"Deleting cluster '{CLUSTER_NAME}'...")
    run(f"kind delete cluster --name {CLUSTER_NAME}", check=False)
    print("Done")


def get_cases():
    return sorted(
        d for d in CASES_DIR.iterdir()
        if d.is_dir() and (d / "aws_state.json").exists() and d.name not in SKIP_CASES
    )


def create_pods(cases):
    """Create all LocalStack pods at once."""
    pods = {}
    for i, case_dir in enumerate(cases):
        case = case_dir.name
        pod = f"ls-{case.replace('case_', '')}"
        port = BASE_PORT + i
        pods[case] = {"pod": pod, "port": port, "dir": case_dir}

        manifest = f"""\
apiVersion: v1
kind: Pod
metadata:
  name: {pod}
  labels:
    app: localstack
    case: {case}
spec:
  containers:
  - name: localstack
    image: localstack/localstack:latest
    ports:
    - containerPort: 4566
    env:
    - name: SERVICES
      value: "iam,s3,ec2,lambda,dynamodb,secretsmanager,sqs"
    readinessProbe:
      httpGet:
        path: /_localstack/health
        port: 4566
      initialDelaySeconds: 5
      periodSeconds: 3
"""
        # Delete if exists, then create
        run(f"kubectl delete pod {pod} --ignore-not-found", check=False)
        p = subprocess.run(
            ["kubectl", "apply", "-f", "-"],
            input=manifest, capture_output=True, text=True,
        )
        if p.returncode != 0:
            print(f"  Failed to create {pod}: {p.stderr.strip()}")
        else:
            print(f"  Created {pod} (case={case}, port={port})")

    return pods


def wait_for_pods(pods, timeout=180):
    """Wait for all pods to be Running+Ready."""
    names = [v["pod"] for v in pods.values()]
    print(f"Waiting for {len(names)} pods (timeout {timeout}s)...")
    start = time.time()
    ready = set()
    while time.time() - start < timeout and len(ready) < len(names):
        for name in names:
            if name in ready:
                continue
            r = run(
                f"kubectl get pod {name} -o jsonpath='{{.status.containerStatuses[0].ready}}'",
                check=False,
            )
            if r.stdout.strip() == "true":
                ready.add(name)
                print(f"  {name} ready ({len(ready)}/{len(names)})")
        if len(ready) < len(names):
            time.sleep(3)
    not_ready = set(names) - ready
    if not_ready:
        print(f"  TIMEOUT: {not_ready}")
    return ready


def port_forward_and_deploy(pods):
    """Port-forward to each pod, deploy state, return processes."""
    procs = []
    results = []

    for case, info in pods.items():
        pod, port, case_dir = info["pod"], info["port"], info["dir"]
        endpoint = f"http://localhost:{port}"

        # Start port-forward
        proc = subprocess.Popen(
            ["kubectl", "port-forward", pod, f"{port}:4566"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        procs.append(proc)

        # Wait for port-forward
        ok = False
        for _ in range(20):
            try:
                req = urllib.request.Request(f"{endpoint}/_localstack/health")
                with urllib.request.urlopen(req, timeout=2) as resp:
                    if resp.status == 200:
                        ok = True
                        break
            except Exception:
                time.sleep(1)

        if not ok:
            print(f"  {case}: port-forward failed")
            results.append((case, pod, port, 0, 0, 0, "port-forward failed"))
            continue

        # Deploy state
        state = json.loads((case_dir / "aws_state.json").read_text())
        r = deploy_resources(state, endpoint)
        deployed, failed, skipped = len(r["deployed"]), len(r["failed"]), len(r["skipped"])
        status = "ok" if failed == 0 else f"{failed} failed"
        print(f"  {case}: deployed={deployed} failed={failed} skipped={skipped}")
        results.append((case, pod, port, deployed, failed, skipped, status))

    return procs, results


def verify(pods):
    """Verify each pod has the expected resources."""
    print("\nVerifying deployed state...")
    all_ok = True
    for case, info in pods.items():
        port = info["port"]
        case_dir = info["dir"]
        endpoint = f"http://localhost:{port}"
        state = json.loads((case_dir / "aws_state.json").read_text())

        errors = []

        # Check IAM policies exist
        try:
            from risk_generator.deployer import get_client
            iam = get_client("iam", endpoint)
            expected_policies = [
                p.get("PolicyName") or p.get("name") or p.get("policy_name")
                for p in state.get("iam", {}).get("policies", [])
            ]
            resp = iam.list_policies(Scope="Local")
            actual = {p["PolicyName"] for p in resp["Policies"]}
            for name in expected_policies:
                if name and name not in actual:
                    errors.append(f"missing policy: {name}")
        except Exception as e:
            errors.append(f"iam check failed: {e}")

        # Check S3 buckets exist
        try:
            s3 = get_client("s3", endpoint)
            expected_buckets = [
                b.get("Name") or b.get("name")
                for b in state.get("s3", {}).get("buckets", [])
            ]
            resp = s3.list_buckets()
            actual = {b["Name"] for b in resp["Buckets"]}
            for name in expected_buckets:
                if name and name not in actual:
                    errors.append(f"missing bucket: {name}")
        except Exception as e:
            errors.append(f"s3 check failed: {e}")

        # Check Lambda functions exist
        try:
            lam = get_client("lambda", endpoint)
            expected_fns = [
                f.get("FunctionName") or f.get("function_name") or f.get("name")
                for f in state.get("lambda", {}).get("functions", [])
            ]
            resp = lam.list_functions()
            actual = {f["FunctionName"] for f in resp["Functions"]}
            for name in expected_fns:
                if name and name not in actual:
                    errors.append(f"missing lambda: {name}")
        except Exception as e:
            errors.append(f"lambda check failed: {e}")

        # Check SGs have ingress rules
        try:
            ec2 = get_client("ec2", endpoint)
            resp = ec2.describe_security_groups()
            actual_sgs = {sg["GroupName"]: sg for sg in resp["SecurityGroups"]}
            for sg_def in state.get("ec2", {}).get("security_groups", []):
                sg_name = sg_def.get("GroupName") or sg_def.get("group_name") or sg_def.get("name")
                if sg_name and sg_name in actual_sgs:
                    expected_rules = sg_def.get("IngressRules") or sg_def.get("ingress_rules") or []
                    actual_rules = actual_sgs[sg_name].get("IpPermissions", [])
                    if expected_rules and not actual_rules:
                        errors.append(f"sg {sg_name}: no ingress rules deployed")
        except Exception as e:
            errors.append(f"ec2 check failed: {e}")

        if errors:
            print(f"  {case}: ISSUES")
            for e in errors:
                print(f"    - {e}")
            all_ok = False
        else:
            print(f"  {case}: OK")

    return all_ok


def main():
    if "--clean" in sys.argv:
        delete_cluster()
        return

    # 1. Cluster
    print("=" * 60)
    print("1. Kind cluster")
    print("=" * 60)
    create_cluster()

    # 2. Cases
    cases = get_cases()
    print(f"\nFound {len(cases)} cases\n")

    # 3. Create pods
    print("=" * 60)
    print("2. Create LocalStack pods")
    print("=" * 60)
    pods = create_pods(cases)

    # 4. Wait
    print("\n" + "=" * 60)
    print("3. Wait for pods")
    print("=" * 60)
    wait_for_pods(pods)

    # 5. Deploy state
    print("\n" + "=" * 60)
    print("4. Deploy AWS state")
    print("=" * 60)
    procs, results = port_forward_and_deploy(pods)

    # 6. Verify
    print("\n" + "=" * 60)
    print("5. Verify")
    print("=" * 60)
    all_ok = verify(pods)

    # 7. Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"\n{'Case':<20} {'Pod':<18} {'Port':<7} {'Deployed':<9} {'Status'}")
    print("-" * 70)
    for case, pod, port, deployed, failed, skipped, status in results:
        print(f"{case:<20} {pod:<18} {port:<7} {deployed:<9} {status}")

    print("\nPort-forward commands (already running):\n")
    for case, info in pods.items():
        print(f"  kubectl port-forward {info['pod']} {info['port']}:4566  # {case}")

    print(f"\nVerify any case:")
    for case, info in pods.items():
        print(f"  curl -s http://localhost:{info['port']}/_localstack/health | python3 -m json.tool")
        break
    print("  ...")

    print(f"\nCleanup:")
    print(f"  uv run python scripts/debug_cases.py --clean")

    if not all_ok:
        print("\nSome verifications failed. Check output above.")

    print(f"\nPort-forwards active. Ctrl+C to stop.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping port-forwards...")
        for p in procs:
            p.terminate()
        print("Pods still running. Use --clean to tear down.")


if __name__ == "__main__":
    main()
