---
license: mit
task_categories:
  - text-generation
language:
  - en
tags:
  - aws
  - security
  - infrastructure
  - due-diligence
  - private-equity
  - localstack
size_categories:
  - n<1K
---

# AWS Technology Risk Cases for PE Due Diligence

Synthetic AWS infrastructure audit cases for evaluating AI agents that detect technology risks during private equity due diligence.

## Dataset Description

Each row is a fictional company with a realistic AWS infrastructure state containing intentionally injected security and operational risks. Designed for benchmarking automated infrastructure auditing agents.

**10 cases** across 5 domains (fintech, ecommerce, devtools, SaaS, healthtech), 3 company sizes, and 10 risk categories.

## Fields

| Field | Type | Description |
|-------|------|-------------|
| `case_id` | string | Unique case identifier |
| `company_name` | string | Fictional company name |
| `domain` | string | Industry vertical |
| `size` | string | small / medium / large |
| `aws_accounts` | int | Number of AWS accounts |
| `has_kubernetes` | bool | Whether company uses K8s |
| `risk_categories` | string | Comma-separated risk codes (e.g. tr1,tr4) |
| `aws_state` | string (JSON) | Full AWS resource state snapshot |
| `risks` | string (YAML) | Ground truth risk labels with severity and business context |
| `narrative` | string (markdown) | Business narrative explaining how risks accumulated |
| `diagram` | string (markdown) | Mermaid infrastructure diagram |

## Usage

```python
from datasets import load_dataset
import json, yaml

ds = load_dataset("koml/agent-tech-risk-cases")

case = ds["train"][0]
aws_state = json.loads(case["aws_state"])
risks = yaml.safe_load(case["risks"])
```

## Risk Categories

| Code | Name | LocalStack Free |
|------|------|----------------|
| tr1 | IAM Overprivilege | Yes |
| tr2 | Secrets Exposure | Yes |
| tr3 | Storage Misconfiguration | Yes |
| tr4 | Network Exposure | Yes |
| tr5 | Multi-Account Sprawl | Yes |
| tr8 | Capacity Gaps | Yes |
| tr9 | Low SLA | Yes |
| tr13 | Outdated Stack | Yes |
| tr14 | Observability Gaps | Yes |
| tr15 | Resource Hygiene | Yes |

## LocalStack Compatibility

All cases use only LocalStack free-tier services: IAM, S3, EC2, Lambda, DynamoDB, SecretsManager, SQS. No RDS, EKS, ElastiCache, or other Pro-only services.

## Source

Generated with [agent-tech-risk](https://github.com/kyryl-opens-ml/ai-engineering/tree/main/blog-posts/agent-tech-risk) using Claude via Agent SDK.
