from dataclasses import dataclass


@dataclass
class RiskCategory:
    code: str
    name: str
    description: str
    aws_resources: list[str]
    example_issues: list[str]
    localstack_free: bool = True


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
        aws_resources=["lambda_function", "secretsmanager_secret", "ssm_parameter"],
        example_issues=[
            "Database credentials in Lambda env vars as plaintext",
            "API keys in SecretsManager without rotation",
            "Hardcoded passwords in environment variables",
        ],
    ),
    "tr3": RiskCategory(
        code="tr3",
        name="Storage Misconfiguration",
        description="Public buckets, missing encryption, no versioning",
        aws_resources=["s3_bucket", "dynamodb_table"],
        example_issues=[
            "S3 bucket with public access enabled",
            "DynamoDB table without SSE encryption",
            "S3 bucket without versioning for critical data",
        ],
    ),
    "tr4": RiskCategory(
        code="tr4",
        name="Network Exposure",
        description="Open security groups, unrestricted ingress on sensitive ports",
        aws_resources=["security_group", "vpc"],
        example_issues=[
            "Security group allowing 0.0.0.0/0 on SSH (22)",
            "Database port (5432/3306) open to the internet",
            "All ports open in development security group",
        ],
    ),
    "tr5": RiskCategory(
        code="tr5",
        name="Multi-Account Sprawl",
        description="Uncontrolled account proliferation, cross-account trust issues",
        aws_resources=["iam_role", "iam_policy"],
        example_issues=[
            "Cross-account roles with wildcard Principal",
            "No SCPs or guardrails across accounts",
            "Shared credentials across environments",
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
        localstack_free=False,
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
        localstack_free=False,
    ),
    "tr8": RiskCategory(
        code="tr8",
        name="Capacity Gaps",
        description="Under-provisioned resources, wrong instance types",
        aws_resources=["ec2_instance", "lambda_function"],
        example_issues=[
            "t2.micro for production workloads",
            "Lambda with 128MB memory causing timeouts",
            "No reserved capacity for steady workloads",
        ],
    ),
    "tr9": RiskCategory(
        code="tr9",
        name="Low SLA",
        description="No backups, no DR plan, missing redundancy",
        aws_resources=["dynamodb_table", "s3_bucket"],
        example_issues=[
            "DynamoDB point-in-time recovery disabled",
            "S3 versioning suspended on critical data",
            "No cross-region replication for key data",
        ],
    ),
    "tr10": RiskCategory(
        code="tr10",
        name="Performance Issues",
        description="Missing caching, wrong instance types, inefficient configs",
        aws_resources=["elasticache_cluster", "cloudfront_distribution"],
        example_issues=[
            "No ElastiCache despite heavy reads",
            "CloudFront not configured for static assets",
            "No read replicas under load",
        ],
        localstack_free=False,
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
        localstack_free=False,
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
        localstack_free=False,
    ),
    "tr13": RiskCategory(
        code="tr13",
        name="Outdated Stack",
        description="EOL runtimes, old AMIs, deprecated services",
        aws_resources=["lambda_function", "ec2_instance"],
        example_issues=[
            "Python 3.8 Lambda (EOL)",
            "Node.js 14.x Lambda (EOL)",
            "AMIs older than 12 months",
        ],
    ),
    "tr14": RiskCategory(
        code="tr14",
        name="Observability Gaps",
        description="No logging, missing metrics, no alerting",
        aws_resources=["cloudwatch_alarm", "lambda_function"],
        example_issues=[
            "No CloudWatch alarms for critical Lambda functions",
            "Lambda functions without error alerting",
            "No structured logging configured",
        ],
    ),
    "tr15": RiskCategory(
        code="tr15",
        name="Resource Hygiene",
        description="Orphaned resources, missing tags, waste",
        aws_resources=["ec2_instance", "s3_bucket", "lambda_function"],
        example_issues=[
            "Lambda functions not invoked in 90+ days",
            "Resources without Owner/Environment tags",
            "Stopped EC2 instances for 90+ days",
        ],
    ),
}


# Categories deployable on LocalStack free tier
LOCALSTACK_FREE_CATEGORIES = [
    code for code, cat in RISK_CATEGORIES.items() if cat.localstack_free
]


def get_category(code: str) -> RiskCategory:
    if code not in RISK_CATEGORIES:
        raise ValueError(f"Unknown risk category: {code}")
    return RISK_CATEGORIES[code]


def list_categories() -> list[RiskCategory]:
    return list(RISK_CATEGORIES.values())
