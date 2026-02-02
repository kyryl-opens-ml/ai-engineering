# PayFlow Infrastructure Narrative

## Company Background

PayFlow is a growing fintech company founded in 2019, specializing in B2B payment processing and financial data analytics. Starting as a small team of 8 engineers, the company has rapidly scaled to 50 engineers across development, data science, and infrastructure teams.

## Growth Journey

### Phase 1: Startup (2019-2020)
- Initial team focused on rapid feature development
- Single AWS account with basic security practices
- Heavy use of broad IAM permissions to move fast
- Manual deployments and minimal infrastructure automation

### Phase 2: Scale-Up (2020-2022)
- Customer base grew 10x, requiring infrastructure scaling
- Team doubled every 6 months during peak growth
- Remote work adoption during COVID led to relaxed network security
- Added development and staging environments
- Began exploring acquisition opportunities, leading to cross-account access needs

### Phase 3: Current State (2022-Present)
- 50 engineers across multiple teams and time zones
- Processing $2M+ in payments daily
- Compliance requirements increasing with enterprise customers
- Technical debt accumulating from rapid growth period
- Security team of 2 people added recently

## How Security Issues Accumulated

### IAM Overprivilege (tr1)
The company's "move fast" culture led to several IAM anti-patterns:

- **DeveloperFullAccess Policy**: Created during a critical product launch when developers were blocked by permission issues. The CTO approved blanket permissions with the intention to refine later, but this never happened due to competing priorities.

- **PayFlowDevRole Cross-Account Trust**: During acquisition discussions with a larger fintech company, the team set up cross-account access. The wildcard principal was used as a "temporary" solution to test integrations, but the deal fell through and the configuration was forgotten.

- **Lambda Overpermissions**: As the company added more data processing functions, each Lambda needed access to different S3 buckets. Rather than manage individual bucket permissions, the team granted broad S3 access "until we have time to implement proper resource-specific policies."

- **Data Processing Permissions**: The analytics team needed to build ETL pipelines connecting various AWS services. Time pressure to deliver customer insights led to granting expansive permissions across S3, RDS, and DynamoDB.

### Network Exposure (tr4)
Network security issues stem from operational pressures and remote work:

- **Development SSH Access**: When the company went remote during COVID, developers needed to access development servers from various locations. The security group was opened to 0.0.0.0/0 as a "temporary measure" for two weeks, but with no central tracking, it remained open for over a year.

- **Public RDS Access**: The business intelligence team needed to connect external analytics tools (Looker, Tableau) to the production database. Setting up private connectivity through VPC peering or VPN was estimated at 2 weeks of infrastructure work. Under pressure to deliver quarterly board reports, the database was made publicly accessible with plans to "secure it properly next quarter."

## Team Structure and Constraints

### Current Team Structure
- **Infrastructure Team**: 3 engineers (hired in last 8 months)
- **Security Team**: 2 engineers (hired in last 4 months)
- **Development Teams**: 45 engineers across 6 product teams
- **Leadership**: CTO + 4 Engineering Managers

### Key Constraints
1. **Technical Debt Backlog**: 200+ security and infrastructure improvements identified
2. **Competing Priorities**: New feature development vs. security hardening
3. **Knowledge Gaps**: Many configurations were set up by engineers who have since left
4. **Process Maturity**: Recently implementing formal change management and security reviews
5. **Compliance Timeline**: SOC 2 Type II audit scheduled for Q3, driving current security initiative

## Current Remediation Efforts

The newly formed security team has begun addressing these issues:
- Conducting quarterly access reviews
- Implementing least-privilege IAM policies
- Planning network segmentation project
- Establishing security guardrails for new infrastructure

However, the team is balancing security improvements with the need to maintain velocity on product development that drives revenue growth. The upcoming due diligence process has provided additional urgency to address the most critical security gaps.