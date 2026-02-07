# QuickCart AWS Infrastructure Due Diligence Report

## Company Overview

**QuickCart** was founded in 2019 by former Amazon engineers Sarah Chen (CEO) and Marcus Rodriguez (CTO) to build a next-generation ecommerce platform targeting mid-market retailers. The company provides white-label ecommerce solutions that enable traditional retailers to compete with Amazon through advanced inventory management, personalized recommendations, and seamless omnichannel experiences.

QuickCart serves over 2,400 retail customers across fashion, electronics, and home goods verticals, processing $1.2B in gross merchandise volume annually. Notable customers include regional chains like MidWest Home & Garden (47 locations) and premium brands like Artisan Leather Co.

## Growth Timeline & Technical Evolution

### 2019-2020: MVP & Early Scaling
- **Founded**: March 2019 with $2M seed funding from Benchmark Capital
- **Initial team**: 12 engineers, all hands-on coding including founders
- **Architecture**: Monolithic Rails app on AWS, single production account
- **Key decision**: Prioritized speed over security - IAM policies used wildcards (*:*) for rapid deployment
- **Milestone**: 50 customers by end of 2019, $5M ARR

The founding team's "move fast and break things" mentality led to overly permissive IAM policies like `QuickCartFullAccess` that granted unlimited AWS access. The CTO created personal admin accounts for quick deployments, a pattern that persisted as the team grew.

### 2021: Hypergrowth & Infrastructure Strain
- **Series A**: $18M led by Index Ventures (February 2021)
- **Team growth**: 12 → 85 engineers across 6 squads
- **COVID impact**: 300% increase in online shopping drove rapid customer acquisition
- **Black Friday crisis**: Site outages during peak traffic exposed infrastructure gaps
- **Emergency fixes**: Opened security groups to "0.0.0.0/0" for debugging access during incidents

The Black Friday 2021 incident was pivotal - under extreme pressure, the platform team created the `quickcart-dev-all-open` security group with unrestricted access to rapidly diagnose performance issues. This "temporary" fix became permanent as the team focused on customer-facing features over infrastructure cleanup.

### 2022: Series B & Acquisition Complexity
- **Series B**: $45M led by Andreessen Horowitz (March 2022)
- **Team size**: 85 → 200 engineers, new VP of Engineering hired
- **Major acquisition**: Purchased competitor "FastShop" for $25M to acquire enterprise customers
- **Integration challenges**: Needed cross-account access for data migration, created overly permissive trust policies
- **CFO pressure**: Q4 cost optimization mandate led to downsizing production instances

The FastShop acquisition created significant technical debt. The integration team had 90 days to migrate 15TB of customer data and maintain business continuity. They created the `QuickCartCrossAccountAdmin` role with wildcard trust policies to expedite access. The integration succeeded, but cleanup was deferred indefinitely.

Cost pressure led to the infamous "t2.micro incident" where the CFO mandated 20% infrastructure savings. The platform team reluctantly downsized the production API server from c5.large to t2.micro, causing widespread performance issues that weren't correlated until customer complaints spiked months later.

### 2023-Present: Scale & Compliance Pressure
- **Current state**: 300+ engineers, 12 AWS accounts, $85M ARR
- **New customers**: Enterprise deals require SOC 2 compliance and security audits
- **Regulatory focus**: PCI DSS requirements for payment processing
- **Technical debt awareness**: New CISO hired, security team established

## Current Engineering Organization

- **Total engineering**: 312 people across 15 squads
- **Platform/Infrastructure**: 18 engineers (6% of total)
- **Security team**: 4 engineers (hired in late 2022)
- **DevOps maturity**: Mixed - some squads use GitOps, others still SSH to production
- **AWS expertise**: Concentrated in 3-4 senior engineers, most teams lack cloud native experience

The security team was only established after enterprise customers began requiring security questionnaires. The CISO discovered the extent of technical debt during their first infrastructure audit in Q1 2023 but has been understaffed to address systemic issues.

## Risk Analysis by Category

### IAM Overprivilege (Critical Priority)
The most severe risks stem from the founding team's "fast deployment" philosophy that persisted through hypergrowth:

- **Root cause**: Original `QuickCartFullAccess` policy was never decomposed as the team specialized
- **Blast radius**: 200+ engineers have indirect access to admin privileges through shared deployment accounts
- **Business impact**: Any compromise could affect all AWS accounts and customer data
- **Acquisition context**: FastShop integration required emergency cross-account access, creating permanent security holes

### Network Exposure (High Priority)
Network security suffered during crisis-driven development cycles:

- **Black Friday syndrome**: The November 2021 outages created a culture of "open first, secure later"
- **Remote work impact**: COVID-19 work-from-home rushed SSH access without proper VPN infrastructure
- **Due diligence pressure**: Series B investors needed database access, leading to internet-exposed databases

### Capacity & Performance (Medium Priority)
Resource right-sizing was sacrificed for short-term cost optimization:

- **CFO mandate**: 20% cost reduction in Q4 2022 led to aggressive downsizing without performance testing
- **Lambda defaults**: Functions created in 2020 never had memory limits adjusted as workloads grew
- **Technical debt**: Performance optimization was consistently deprioritized for new features

### Resource Hygiene (Medium Priority)
Rapid scaling and acquisitions created operational entropy:

- **Acquisition aftermath**: FastShop integration created numerous orphaned resources with unclear ownership
- **Tagging inconsistency**: Standards defined in 2022 but never retroactively applied
- **No cleanup culture**: "Better safe than sorry" mentality prevented proactive resource management

## Post-Acquisition Remediation Requirements

A private equity buyer should budget 6-12 months and $2-3M for infrastructure remediation:

### Immediate (0-90 days)
- **IAM overhaul**: Implement least-privilege policies, eliminate wildcard permissions
- **Network segmentation**: Replace open security groups with proper VPC design
- **Secrets management**: Migrate hardcoded credentials to AWS Secrets Manager
- **Cost**: ~$800K (2 security consultants + 6 months platform team focus)

### Medium-term (3-9 months)
- **Capacity optimization**: Right-size instances, implement auto-scaling
- **Resource cleanup**: Remove orphaned resources, implement tagging standards
- **Backup & disaster recovery**: Implement cross-region backups for critical data
- **Cost**: ~$1.2M (infrastructure team expansion + tooling)

### Long-term (9-18 months)
- **Multi-account strategy**: Separate production/staging/development environments
- **Compliance frameworks**: SOC 2, PCI DSS certification
- **Infrastructure as Code**: Migrate to Terraform/CloudFormation for governance
- **Cost**: ~$1.5M (dedicated compliance team + external auditors)

## Competitive Context

QuickCart's infrastructure debt is typical for hypergrowth B2B SaaS companies but more severe than best-in-class peers:

- **Shopify**: Underwent similar remediation in 2018-2019, invested $50M in infrastructure rebuild
- **WooCommerce**: Has more mature security practices due to WordPress ecosystem requirements
- **BigCommerce**: Smaller scale but higher security baseline from enterprise focus

The good news: QuickCart's core architecture is sound, and the team has strong engineering talent. The security issues are primarily configurational rather than fundamental design flaws.

## Investment Recommendation

QuickCart represents a **moderate-risk** infrastructure investment requiring significant but manageable remediation:

**Strengths:**
- Strong revenue growth and customer retention
- Experienced engineering leadership aware of technical debt
- Modern cloud-native architecture with good bones
- Recently hired CISO demonstrates security commitment

**Risk Mitigation:**
- Budget $2-3M for 12-month security remediation program
- Hire dedicated DevSecOps team (4-6 engineers)
- Implement phased approach prioritizing critical security issues
- Consider cyber insurance premium increases during remediation period

The infrastructure risks are solvable with proper investment and execution. QuickCart's strong market position justifies the remediation costs, and the company is well-positioned for continued growth post-cleanup.