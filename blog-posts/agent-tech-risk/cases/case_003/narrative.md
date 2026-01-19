# MedData Technical Due Diligence - Company Narrative

## Company Background

**MedData** is a healthtech company founded in 2019 that provides a cloud-based platform for hospital systems to aggregate, analyze, and share patient data across care networks. The company started with a single hospital client in Boston and has grown to serve 47 hospital systems across the Northeast and Mid-Atlantic regions.

The platform processes HL7 and FHIR messages from Electronic Medical Records (EMR) systems, performs real-time risk scoring for patient readmission, and provides analytics dashboards for care coordination teams.

## Growth Timeline

### 2019-2021: Startup Phase
- Founded by 3 engineers and 2 healthcare industry veterans
- Initial architecture: Monolithic Ruby on Rails app on Heroku
- 8 engineers, single AWS account
- First customer: Boston Memorial Hospital (150 beds)

### 2022: Series A ($18M)
- Grew to 45 engineers
- Major customer win: Northeast Health Network (12 hospitals, 3,500 beds)
- Migrated from Heroku to AWS
- Platform team of 5 built initial AWS infrastructure
- Made architectural decision to use EKS for microservices
- Hired VP Engineering from prior healthtech unicorn

### 2023: Rapid Expansion
- Series B ($65M) in March
- Grew from 45 to 180 engineers
- Won contracts with 3 major hospital systems
- Epic EMR integration became critical path (80% of hospitals use Epic)
- Massive hiring across engineering org: 6 new engineering teams formed
- First DevOps engineer hired in April (previously all platform work done by full-stack engineers)

### 2024: Scaling Pains
- Grew to 280 engineers across 15 teams
- Multiple AWS accounts created for compliance (prod, staging, dev, DR, analytics, ML, security)
- HIPAA compliance audit revealed technical debt
- Legacy MySQL database from 2019 still running, scheduled for migration
- Cost optimization initiatives led to some infrastructure decisions (disabled backups, removed replication)
- VP Engineering left for FAANG company, replaced in September

### 2025-Present: Consolidation
- 350 engineers, growth slowing
- Focus on operational excellence and profitability
- Platform team of 25 engineers managing infrastructure
- Security team of 8 conducting remediation efforts
- Series C planned for Q3 2026, technical due diligence expected

## Technical Organization Structure

### Platform Team (25 engineers)
- **EKS/Kubernetes**: 6 engineers (hired 2023-2024, varying K8s experience)
- **DevOps/CI-CD**: 5 engineers (manage Jenkins, Terraform, AWS infrastructure)
- **Data Infrastructure**: 8 engineers (RDS, S3, data pipelines)
- **SRE**: 6 engineers (monitoring, incident response)

### Product Engineering (280 engineers)
- **API Team**: 35 engineers (FastAPI microservices on EKS)
- **Integration Team**: 45 engineers (HL7, FHIR, EMR integrations)
- **ML Team**: 40 engineers (risk scoring models, predictions)
- **Analytics Team**: 30 engineers (dashboards, reporting)
- **Data Engineering**: 35 engineers (ETL, data warehouse)
- **Mobile Team**: 25 engineers (iOS, Android apps)
- **Frontend Team**: 40 engineers (React dashboard)
- **Legacy Systems**: 12 engineers (maintaining old services, migration work)
- **QA/Test**: 18 engineers

### Security & Compliance (8 engineers)
- **Security Engineering**: 5 engineers
- **Compliance**: 3 engineers (HIPAA, SOC 2)

## Why Technical Debt Accumulated

### 1. Hypergrowth Phase (2023)
The company grew from 45 to 180 engineers in a single year while simultaneously:
- Winning largest customers requiring immediate Epic integration
- Hiring entire teams of junior and mid-level engineers
- Building new features faster than infrastructure could scale properly
- Operating under extreme pressure to meet hospital go-live dates

**Impact**: Integration team cut corners on secrets management to meet Epic go-live deadline. HL7 processor Lambda was deployed with hardcoded credentials because Secrets Manager integration would have added 2 weeks to timeline.

### 2. Knowledge Gaps and Turnover
- First DevOps engineer hired April 2023, left August 2024
- Platform team grew quickly but many had traditional web background, not cloud-native
- EKS cluster setup followed tutorial that bound cluster-admin to default service account
- Original security assumptions not revisited as use cases evolved

**Impact**: Kubernetes RBAC misconfiguration went unnoticed. Team knew it was wrong but fixing it became increasingly risky as more services depended on it. "We'll fix it in the next cluster rebuild" became permanent deferral.

### 3. Legacy System Inertia
The original MySQL database from 2019 was supposed to be migrated in Q1 2024. The engineer leading the migration left the company in December 2023. The replacement engineer found the migration plan incomplete and data-sync Lambda full of undocumented edge cases.

**Impact**: Legacy database and its temporary sync Lambda (with embedded credentials) remain in production. Each quarter, migration is re-scheduled. Nobody wants ownership of the risky migration.

### 4. Cost Optimization Pressures
In mid-2024, the company missed revenue targets. Finance demanded 30% infrastructure cost reduction. Platform team made several quick decisions:
- Disabled backups on analytics read replica (saved $2K/month in storage)
- Removed cross-region replication for S3 buckets (saved $8K/month in data transfer)
- Delayed EKS upgrades to avoid testing costs

**Impact**: DR posture weakened. Analytics database, originally non-critical, was later repurposed for executive dashboards without reconsidering backup policy.

### 5. Security vs. Velocity Trade-offs
The Integration Engineering team operates under constant pressure from hospital clients with strict go-live dates. Missing a go-live date means contract penalties and potential customer loss.

**Impact**:
- Epic API key stored as plain String in SSM instead of SecureString (team didn't know the difference)
- FHIR API key in Lambda env vars instead of Secrets Manager (team claimed cold start latency was issue, but real reason was lack of time to implement properly)
- Encryption keys for HL7 messages stored in env vars (compliance requirement added last-minute)

### 6. Incomplete Kubernetes Expertise
The Platform team adopted Kubernetes in 2022 when it was the "right" choice for a modern cloud architecture. However:
- Initial team had 2 weeks of K8s experience before going to production
- Followed tutorials and copy-pasted YAML without deep understanding
- NetworkPolicies were "phase 2" and never implemented
- Deprecated APIs worked fine, so upgrading them wasn't prioritized
- PodSecurityPolicy was set up before PSP deprecation was announced

**Impact**: Cluster runs with no network segmentation, deprecated APIs, and ineffective security policies. Each fix requires extensive testing that the team doesn't have time for.

### 7. IAM Access Key Rotation Challenges
Jenkins CI/CD pipeline was set up in 2023 using IAM user access keys (before OIDC was well-documented for GitHub Actions). Attempting to rotate the key in 2024 broke deployments across 23 repositories.

**Impact**: After failed rotation attempt and 6-hour outage, team decided to "do it properly" with OIDC federation. But Platform team was underwater with other work. Ticket sat in backlog for 18 months while old access key remains active.

### 8. Organizational Silos
- Platform team owns infrastructure but doesn't understand all application requirements
- Integration team owns HL7 processor but doesn't have IAM/KMS expertise
- Security team identifies issues but doesn't have capacity to fix them
- Each team has different priorities and deadlines

**Impact**: Cross-team coordination required for fixes (like migrating secrets to Secrets Manager) never gets scheduled. Each team waiting on the other.

## Current State

As of January 2026, MedData is preparing for Series C fundraising. The technical organization is aware of the accumulated debt and has created remediation plans:

- **Q1 2026**: Kubernetes RBAC redesign (in progress, behind schedule)
- **Q2 2026**: Secrets Manager migration for all Lambda functions (planned)
- **Q2 2026**: Legacy database migration (re-scheduled from Q4 2025)
- **Q3 2026**: DR posture improvements (S3 replication, backup policies)
- **Q4 2026**: IAM access key elimination (OIDC federation)

However, priorities keep shifting based on customer demands and product roadmap. The Platform team is chronically understaffed relative to the demands of 280 product engineers building new features.

## The PE Diligence Context

A private equity firm is conducting technical due diligence ahead of potential Series C participation. They're particularly concerned about:

1. **Security posture** - Given HIPAA requirements and PHI data handling
2. **Operational resilience** - Can the platform handle growth to 200+ hospitals?
3. **Technical debt** - What's the true cost to remediate?
4. **Team capability** - Can current team execute cleanup while maintaining velocity?

The infrastructure described in this dataset represents the real state of the AWS environment that the PE firm's technical consultants are reviewing.
