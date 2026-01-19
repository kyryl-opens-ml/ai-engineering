# PayFlow Infrastructure Narrative

## Company Background

PayFlow is a fintech startup founded in 2021 that provides payment processing infrastructure for small and medium-sized e-commerce businesses. The company experienced rapid growth from 2022-2024, scaling from 15 engineers to 50 while processing $2B+ in annual transaction volume.

**Key Milestones:**
- 2021: Founded, single AWS account, 5 engineers
- 2022: Series A funding ($15M), grew to 20 engineers
- 2023: PCI-DSS certification achieved, 30 engineers
- 2024: Series B funding ($45M), multi-account setup, 50 engineers
- 2025: Preparing for PE due diligence

## Technical Team Structure

**Infrastructure Team (3 engineers)**
- 1 Principal Engineer (inherited legacy decisions)
- 2 Mid-level DevOps Engineers (joined in 2024)

**Product Engineering (40 engineers)**
- Payments Team (12): Core transaction processing
- Risk Team (8): Fraud detection and compliance
- Platform Team (10): Internal tools and APIs
- Data Science Team (5): Analytics and ML models
- Frontend Team (5): Customer-facing applications

**Leadership**
- CTO: Former startup founder, hands-on but overextended
- VP Engineering: Hired in 2024, focused on scaling hiring

## Infrastructure Evolution

### Phase 1: Single Account (2021-2023)
PayFlow started with one AWS account and manual deployments. The founding team prioritized shipping features over infrastructure governance. Everything lived in `us-east-1` in a single VPC.

### Phase 2: Growth Chaos (2023-2024)
During hypergrowth, the team created new AWS accounts reactively:
- **Production account** (123456789012): PCI-DSS audit requirement
- **Development account** (123456789013): Developer sandbox requests
- **Staging account** (123456789014): QA team needed pre-prod environment

The infrastructure team was just 2 people at this time, overwhelmed by feature requests and incident response. Account creation happened quickly without establishing proper governance frameworks.

### Phase 3: Technical Debt Accumulation (2024-2025)
With 50 engineers deploying daily, technical debt accumulated:
- Cross-account access patterns emerged organically
- Container configurations copied from development to production
- Resources created and forgotten during rapid experimentation
- Tagging standards defined but inconsistently applied

## How Issues Accumulated

### Multi-Account Sprawl (TR5)

**The CrossAccountAdminRole Incident:**
In March 2024, a critical production deployment failed at 11 PM during a major customer onboarding. The payments team needed to deploy a hotfix from the development account to production, but proper cross-account roles didn't exist.

The on-call engineer created `CrossAccountAdminRole` with a wildcard trust policy (`"Principal": {"AWS": "*"}`) and full admin access. The deployment succeeded, the customer onboarding completed, and everyone moved on. The post-incident review ticket included "TODO: Fix trust policy" but was marked low priority since "it worked."

The role remains active 10 months later. The infrastructure team discovered it during a routine audit in October 2025 but focused on more visible issues. The CTO approved it as a temporary fix, so no one feels empowered to delete it.

**Missing Service Control Policies:**
When PayFlow created their AWS Organization in early 2024, the infrastructure team planned to implement SCPs as part of their Q4 governance initiative. However, Q4 was dominated by the payment gateway redesign project (revenue-critical feature) and the SCP work was postponed to 2025.

With only 3 infrastructure engineers supporting 50+ developers, governance work consistently loses priority battles against feature delivery and incident response.

### Container Security (TR12)

**Development Environment Privileges:**
PayFlow's data science team works in the staging account, experimenting with ML models for fraud detection. They need to install custom Python packages, system libraries, and occasionally test containerization strategies.

In June 2024, a data scientist couldn't install required dependencies without root access. After 2 days of blocked work, the team lead escalated to the VP of Engineering. The solution: run containers as root with privileged mode enabled.

The infrastructure team pushed back, citing security risks. The data science team argued this was "just staging" and production containers were properly secured. Management sided with unblocking the data team. The compromise: "We'll fix it before production deployment."

The analytics workload never moved to production (it runs in staging processing production data via cross-account S3 access). The container configuration remains privileged.

**Development Container Configuration:**
The dev account's container setup mirrors production for consistency, but developers added privileged mode and root access to install debugging tools without rebuilding images. This pattern became standard practice documented in internal wikis.

### Resource Hygiene (TR15)

**The Orphaned Volume Problem:**
PayFlow has 6+ unattached EBS volumes across accounts, costing ~$50/month combined. Individual breakdown:

1. **vol-orphan001** (June 2024): During a gp2→gp3 migration sprint, an engineer terminated instances but forgot to check "delete on termination" for volumes. No one noticed because the instance was gone.

2. **vol-orphan002** (August 2024): Created during a 2 AM production incident. The on-call engineer was troubleshooting a database connection issue and created a temporary volume for debugging. After resolving the incident, they forgot to clean it up.

3. **vol-orphan003** (September 2024): A DBA created this for testing a database migration. The migration succeeded in October, but they kept the volume "in case we need to rollback." The DBA left the company in November. No one wants to delete it without their approval.

4. **vol-orphan004** (December 2023): The oldest orphan. Predates the current infrastructure team. No documentation exists. Too risky to delete ("what if it breaks something?") but costs only $6/month.

**Tagging Gaps:**
PayFlow formalized their tagging policy in September 2024, requiring `Owner`, `Environment`, and `CostCenter` tags. However, resources created before September aren't consistently tagged.

The infrastructure team created a backlog item: "Retag all legacy resources." It's been in the backlog for 4 months, always deprioritized behind feature work and incidents.

Automated tagging enforcement exists for new resources (via AWS Config), but fixing old resources requires manual work. With 3 infrastructure engineers, it never makes the sprint.

**The Stopped Instance:**
`legacy-test-server` has been stopped since December 2023 to save compute costs, but still incurs EBS charges (~$25/month). The original owner left in May 2024. No one knows what it was for.

The infrastructure team has discussed deleting it three times. Each time, someone says "let's wait one more month to be safe." It's now been 13 months.

## Team Constraints

### Infrastructure Team Capacity
With 3 engineers supporting 50 developers:
- **Reactive vs Proactive:** 70% of time spent on incident response and feature support
- **Context Switching:** Average 15+ Slack interruptions per day
- **Prioritization:** Revenue-critical features always win vs governance work

### Knowledge Gaps
- Principal Engineer joined after multi-account setup was live
- 2 mid-level engineers learning AWS Organizations while managing daily operations
- No dedicated security engineer (security is "everyone's responsibility")

### Management Pressures
- PE due diligence deadline is forcing infrastructure audit
- Customer commitments drive roadmap priorities
- Infrastructure improvements hard to justify to non-technical executives

## Why Issues Persist

1. **Rational Compromise:** Each decision made sense given context and constraints
2. **Invisible Debt:** Technical debt doesn't impact customers until it does
3. **Tragedy of Commons:** No single team owns cross-cutting concerns
4. **Risk Tolerance:** Startup culture accepts technical debt for speed
5. **Capacity Constraints:** Infrastructure team perpetually underwater

## Current State (January 2026)

PayFlow is preparing for PE due diligence. The infrastructure team is suddenly getting executive attention and budget for security improvements. Issues that existed for months are now P0s.

The team is racing to:
- Implement Service Control Policies
- Fix cross-account role trust policies
- Remove container privileged mode
- Clean up orphaned resources
- Retroactively tag legacy infrastructure

They have 6 weeks before the technical assessment.
