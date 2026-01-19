from dataclasses import dataclass


@dataclass
class RiskCategory:
    code: str
    name: str
    description: str
    aws_resources: list[str]
    example_issues: list[str]


RISK_CATEGORIES: dict[str, RiskCategory] = {
    "tr1": RiskCategory(
        code="tr1",
        name="IAM Overprivilege",
        description="Overly permissive IAM policies with wildcards or excessive permissions",
        aws_resources=["iam_role", "iam_policy", "iam_user"],
        example_issues=[
            "Action: * on Resource: *",
            "Cross-account trust with Principal: *",
            "Unused admin roles from early days",
        ],
    ),
    "tr2": RiskCategory(
        code="tr2",
        name="Secrets Exposure",
        description="Secrets in plaintext, no rotation, or exposed in configs",
        aws_resources=["lambda_function", "ssm_parameter", "secretsmanager_secret"],
        example_issues=[
            "Database credentials in Lambda env vars",
            "API keys in SSM without encryption",
            "No secret rotation configured",
        ],
    ),
    "tr3": RiskCategory(
        code="tr3",
        name="Storage Misconfiguration",
        description="Public buckets, missing encryption, exposed snapshots",
        aws_resources=["s3_bucket", "ebs_snapshot", "rds_snapshot"],
        example_issues=[
            "S3 bucket with public ACL",
            "EBS snapshots shared publicly",
            "Missing server-side encryption",
        ],
    ),
    "tr4": RiskCategory(
        code="tr4",
        name="Network Exposure",
        description="Open security groups, public subnets, missing firewalls",
        aws_resources=["security_group", "vpc", "subnet", "nacl"],
        example_issues=[
            "Security group allowing 0.0.0.0/0 on SSH",
            "RDS in public subnet",
            "Missing VPC flow logs",
        ],
    ),
    "tr5": RiskCategory(
        code="tr5",
        name="Multi-Account Sprawl",
        description="Uncontrolled account proliferation, missing governance",
        aws_resources=["organizations_account", "iam_role"],
        example_issues=[
            "12 accounts with no SCPs",
            "Cross-account roles with broad trust",
            "No centralized logging account",
        ],
    ),
    "tr6": RiskCategory(
        code="tr6",
        name="Scaling Limits",
        description="Hardcoded capacity, missing autoscaling, bottlenecks",
        aws_resources=["autoscaling_group", "eks_node_group", "ecs_service"],
        example_issues=[
            "ASG min=max=2 (no scaling)",
            "Hardcoded connection pool sizes",
            "EKS node group at max capacity",
        ],
    ),
    "tr7": RiskCategory(
        code="tr7",
        name="Single Points of Failure",
        description="Single-AZ deployments, no redundancy",
        aws_resources=["rds_instance", "elasticache_cluster", "nat_gateway"],
        example_issues=[
            "RDS with multi_az=false",
            "Single NAT gateway for all traffic",
            "ElastiCache single-node cluster",
        ],
    ),
    "tr8": RiskCategory(
        code="tr8",
        name="Capacity Gaps",
        description="Under-provisioned resources, wrong instance types",
        aws_resources=["ec2_instance", "rds_instance", "lambda_function"],
        example_issues=[
            "t2.micro for production database",
            "Lambda with 128MB memory timeout issues",
            "No reserved capacity for steady workloads",
        ],
    ),
    "tr9": RiskCategory(
        code="tr9",
        name="Low SLA",
        description="No backups, no DR plan, missing redundancy",
        aws_resources=["rds_instance", "dynamodb_table", "s3_bucket"],
        example_issues=[
            "RDS backup_retention_period=0",
            "No cross-region replication",
            "DynamoDB point-in-time recovery disabled",
        ],
    ),
    "tr10": RiskCategory(
        code="tr10",
        name="Performance Issues",
        description="Missing caching, wrong instance types, inefficient configs",
        aws_resources=["elasticache_cluster", "cloudfront_distribution", "rds_instance"],
        example_issues=[
            "No ElastiCache despite heavy reads",
            "CloudFront not configured for static assets",
            "RDS without read replicas under load",
        ],
    ),
    "tr11": RiskCategory(
        code="tr11",
        name="K8s Misconfig",
        description="EKS RBAC issues, deprecated APIs, no network policies",
        aws_resources=["eks_cluster", "eks_node_group"],
        example_issues=[
            "cluster-admin bound to default service account",
            "Using deprecated Kubernetes APIs",
            "No NetworkPolicy resources defined",
        ],
    ),
    "tr12": RiskCategory(
        code="tr12",
        name="Container Security",
        description="Privileged containers, missing resource limits",
        aws_resources=["eks_cluster", "ecs_task_definition"],
        example_issues=[
            "Containers running as root",
            "No CPU/memory limits defined",
            "Images from untrusted registries",
        ],
    ),
    "tr13": RiskCategory(
        code="tr13",
        name="Outdated Stack",
        description="EOL runtimes, old AMIs, deprecated services",
        aws_resources=["lambda_function", "ec2_instance", "eks_cluster"],
        example_issues=[
            "Python 3.8 Lambda (EOL)",
            "EKS running Kubernetes 1.25",
            "AMIs older than 12 months",
        ],
    ),
    "tr14": RiskCategory(
        code="tr14",
        name="Observability Gaps",
        description="No CloudTrail, missing metrics, no alerting",
        aws_resources=["cloudtrail_trail", "cloudwatch_alarm", "config_recorder"],
        example_issues=[
            "CloudTrail not enabled in all regions",
            "No CloudWatch alarms for critical services",
            "AWS Config not recording",
        ],
    ),
    "tr15": RiskCategory(
        code="tr15",
        name="Resource Hygiene",
        description="Orphaned resources, missing tags, waste",
        aws_resources=["ebs_volume", "elastic_ip", "ec2_instance"],
        example_issues=[
            "50+ unattached EBS volumes",
            "Resources without Owner/Environment tags",
            "Stopped EC2 instances for 90+ days",
        ],
    ),
}


def get_category(code: str) -> RiskCategory:
    if code not in RISK_CATEGORIES:
        raise ValueError(f"Unknown risk category: {code}")
    return RISK_CATEGORIES[code]


def list_categories() -> list[RiskCategory]:
    return list(RISK_CATEGORIES.values())
