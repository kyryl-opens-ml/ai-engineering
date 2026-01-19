# PayFlow: Company Background and Technical Evolution

## Company Overview

**PayFlow** is a fintech startup that provides payment processing infrastructure for small-to-medium businesses. Founded in early 2023, the company offers a developer-friendly API for accepting payments, managing subscriptions, and detecting fraud.

- **Founded**: Q1 2023
- **Funding**: Seed round ($3.5M) in mid-2023, currently raising Series A
- **Team Size**: 50 employees (25 engineering, 8 product, 10 sales, 7 ops/admin)
- **Revenue**: ~$2M ARR, processing $50M in payments annually
- **Customers**: 450 active merchants

## Growth Timeline

### Phase 1: MVP Launch (Q1-Q2 2023)

The founding team consisted of a CTO (ex-Stripe engineer), CEO (former fintech product manager), and three engineers. They built the MVP on AWS with a focus on speed over perfection:

- Single AWS account
- Manual deployments via AWS Console
- Basic API on EC2 instances
- PostgreSQL RDS for transaction data
- S3 for logging

The CTO created the `DevOpsFullAccess` policy during the first week to unblock the team. "We'll tighten this up after launch" became a recurring phrase. Launch happened in 6 weeks.

### Phase 2: Scaling Up (Q3 2023 - Q2 2024)

After closing their seed round, PayFlow hired rapidly:
- Engineering grew from 3 to 15
- First dedicated infrastructure engineer joined in September 2023
- Added staging environment (second AWS account)
- Implemented CI/CD with GitHub Actions and the `deploy-bot` service account

The infrastructure team (2 people by this point) focused on:
- Setting up proper VPC networking
- Moving to infrastructure-as-code (Terraform)
- Adding monitoring and alerting
- Implementing zero-downtime deployments

However, fundamental architectural decisions were "too risky to change with production traffic." The single-AZ database stayed single-AZ. The overprivileged IAM policies remained because "we need to refactor the entire IAM structure, and we don't have time right now."

### Phase 3: Compliance Push (Q3 2024 - Present)

With Series A discussions heating up, potential investors asked for SOC 2 compliance. PayFlow hired a security consultant who:
- Conducted infrastructure audit
- Identified critical issues (including the IAM overprivileges)
- Recommended multi-AZ for production databases
- Set up cross-account auditor role for compliance audits

The auditor role setup was rushed. The consultant left detailed documentation in a Notion page titled "Auditor Access Setup" with the ExternalId clearly visible. The page is accessible to all engineering team members.

Meanwhile, the data science team (hired in mid-2024) needed ML capabilities:
- Stood up SageMaker for fraud detection models
- Created dedicated ML workstation on EC2
- Built analytics database (single-AZ, "non-critical")
- Requested broad S3/SageMaker permissions "to experiment efficiently"

The infrastructure team granted the broad permissions because:
1. It was only 3 people on the data science team
2. The CTO personally trusted them
3. Managing granular permissions seemed like overkill
4. They were under pressure to ship the fraud detection feature for a major customer

## Why Issues Accumulated

### Cost Consciousness
As a seed-stage startup burning ~$250K/month, every AWS dollar mattered. Multi-AZ RDS would add ~$5K/year. A second NAT Gateway would add ~$400/year. These seemed like luxuries when the team was optimizing for runway.

### Speed Over Security
The product roadmap was aggressive. Investors expected 3x customer growth before Series A. The engineering team prioritized:
1. Customer-facing features
2. System reliability
3. Developer experience
4. Security hardening ← always deprioritized

### Knowledge Gaps
The infrastructure team consisted of:
- One senior engineer (solid AWS knowledge but new to fintech compliance)
- One mid-level engineer (great at Terraform but limited security experience)

Neither had experience with:
- Compliance frameworks (SOC 2, PCI DSS)
- Large-scale fintech infrastructure
- Security architecture reviews

They knew the IAM policies were overprivileged but didn't fully understand the blast radius.

### "We'll Fix It Later" Culture
The CTO, coming from a big tech background, assumed they'd have time to refactor. At Stripe, there were dedicated security and infrastructure teams. At PayFlow, the infra team was constantly firefighting:
- Scaling issues as customer volume grew
- Weekly production incidents
- New feature requests from customers
- Investor due diligence requests

Technical debt kept accumulating with plans to "clean it up after Series A when we hire more people."

### Organizational Structure

```
CEO
├── CTO (John Smith - AdministratorAccess)
│   ├── Engineering Manager
│   │   ├── Backend Team (8 engineers)
│   │   ├── Frontend Team (5 engineers)
│   │   └── Mobile Team (3 engineers)
│   ├── Infrastructure Team (2 engineers)
│   │   ├── Senior Infrastructure Engineer
│   │   └── DevOps Engineer
│   └── Data Science Team (3 people)
│       ├── ML Engineer
│       ├── Data Scientist
│       └── Analytics Engineer
├── Product (8 people)
├── Sales (10 people)
└── Operations (7 people)
```

The infrastructure team reports to the CTO but is constantly pulled in different directions:
- Backend team needs new Lambda functions deployed
- Data science needs access to production data
- Product needs staging environments for testing
- Sales needs demo environments for prospects

## Current State (January 2026)

PayFlow is in late-stage Series A discussions. A potential lead investor's technical due diligence team is reviewing the infrastructure. The company is processing $50M in payments annually with customers in financial services, healthcare, and e-commerce.

The engineering team knows there are issues but:
- Multi-AZ migration is scheduled for Q2 2026 ("after Series A closes")
- IAM refactoring is in the backlog ("needs 2-3 weeks of dedicated time")
- The auditor role "should probably be locked down" but no one has prioritized it
- NAT Gateway redundancy was discussed but "we've never had an AZ failure"

Everyone assumes the technical debt is manageable. After all, they haven't had a major security incident yet. The system has been stable. Customers are happy.

The infrastructure team's 2026 roadmap includes:
1. ~~Kubernetes migration~~ (pushed to 2027)
2. ~~Multi-region deployment~~ (not needed yet)
3. Multi-AZ for all critical resources (Q2 2026)
4. IAM hardening (Q2 2026)
5. PCI DSS compliance prep (Q3 2026)

The question is: will they get there before something breaks?
