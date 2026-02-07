# InsureNet AWS Infrastructure Audit - Due Diligence Report

## Company Background

InsureNet was founded in 2019 by three former McKinsey consultants who identified inefficiencies in small business insurance underwriting. The company builds AI-powered risk assessment tools that help regional insurers price policies for restaurants, retail stores, and service businesses. Their flagship product processes over 50,000 insurance quotes monthly, analyzing everything from foot traffic patterns to local crime statistics.

InsureNet sells primarily to mid-market insurance carriers ($50M-$500M in premiums) who lack the technology sophistication of larger players like State Farm or Allstate. Their average customer is a 75-year-old mutual insurance company in the Midwest that still uses spreadsheets for underwriting.

## Growth Timeline & Technical Evolution

**2019-2020: Scrappy Startup Phase**
- Founded with $2M seed round, team of 3 engineers
- Built MVP on single AWS account with full admin access for everyone
- Created `InsureNet-FullAccess` policy for rapid deployment - "We'll fix permissions later"
- Reached $500K ARR with 12 insurance carrier clients

**2021: Series A Growth ($8M raised)**
- Scaled to 25 engineers after acquiring a smaller insurtech competitor
- Added 5 more AWS accounts during acquisition integration
- Created cross-account access roles with wildcard principals - "We need this working by Monday for the board meeting"
- Launched in 3 new states, grew to $2.8M ARR

**2022: Operational Scaling Challenges**
- Reached 75 engineers, first dedicated DevOps hire
- December production outage during holiday shopping season - their busiest time
- Opened SSH access to internet during emergency response while security team was on vacation
- Infrastructure became increasingly complex with 6 AWS accounts and no central governance
- Ended year at $8M ARR but with technical debt mounting

**2023: Security Awakening ($15M Series B)**
- Hired first CISO and security team of 3 people in March
- Major incident in July: database accidentally exposed to internet during migration
- Started implementing security controls but struggled with legacy systems
- Grew to 150 engineers across 4 offices (Austin, Denver, Chicago, Remote)
- Revenue hit $18M ARR with 45 insurance carriers as customers

**Current State (2024)**
- 150 engineers, 8-person security team, 12-person platform team
- Processing 200,000+ quotes monthly
- 6 AWS accounts: prod, staging, dev, analytics, vendor-integrations, sandbox
- Mix of modern security practices and legacy technical debt

## Why These Risks Exist

### IAM Overprivilege Crisis
The root cause traces back to InsureNet's founding philosophy: "Move fast, fix permissions later." The original `InsureNet-FullAccess` policy was created during a 72-hour sprint to demo for their first major client, a $200M mutual insurer in Iowa. "We had three days to prove we could handle their data volume or lose the contract," recalls the founding CTO.

This policy still powers their deployment pipeline because refactoring would require rewriting infrastructure-as-code across all 6 accounts. The `insurenet-deployer` service account has been unchanged since the CTO's departure in 2020 - rotating it would break deployment scripts that nobody fully understands.

The cross-account trust issues stem from their 2021 acquisition. The acquired company (RiskTech Solutions) had 2 engineers and used completely different AWS patterns. During integration, a junior engineer created wildcard cross-account trusts because "the networking guys said VPC peering was too complicated." The 90-day integration timeline left no room for security reviews.

### Network Exposure Problems
InsureNet's network security issues reflect the classic startup-to-scaleup transition crisis. The SSH exposure on production web servers happened during their worst outage ever - December 23rd, 2022, when a misconfigured load balancer took down quote processing during peak shopping season. "We had insurance agents calling us at 11 PM because they couldn't quote Christmas shoppers," explains their VP of Engineering.

The development environment's "all ports open" configuration spread organically. One frustrated engineer created it during a VPN outage that blocked deployments for 6 hours. Other developers copied the security group because it "just worked." The development team grew from 15 to 60 engineers in 2022, and this configuration became the path of least resistance.

The exposed PostgreSQL database represents their most dangerous near-miss. During a 2023 migration from on-premises to AWS RDS, a junior cloud engineer confused CIDR notation. They meant to allow access from their VPC (10.0.0.0/16) but instead opened it to the entire internet (0.0.0.0/0). The database contained 2.5 million insurance applications with SSNs and financial data. This went undetected for 3 months until discovered during this audit.

### Multi-Account Management Failures
InsureNet's account sprawl reflects their growth-first mentality. Each major milestone triggered new AWS account creation: the Series A acquisition, launching in new states, adding analytics capabilities, onboarding enterprise clients who demanded isolated environments. But they never invested in centralized governance tools like AWS Organizations or Service Control Policies.

The shared API key across environments exemplifies their cost-optimization-over-security mindset during the Series A phase. Their risk scoring vendor charged $5,000 per API key. Using one key across dev, staging, and production saved $10,000 annually - significant for a company burning $500K/month. "We were optimizing for runway extension, not security best practices," admits their former CFO.

## Current Engineering Organization

**Platform Team (12 people):**
- 2 Principal Engineers (both hired in 2023)
- 4 Senior Platform Engineers
- 3 Cloud Engineers
- 2 Site Reliability Engineers
- 1 Platform Manager

**Security Team (8 people):**
- 1 CISO (hired March 2023)
- 2 Security Engineers
- 2 Compliance Engineers (SOC 2 & state insurance regulations)
- 1 Security Architect
- 1 GRC Manager
- 1 Security Operations Manager

**Product Engineering (130 people):**
- 8 teams of 12-15 engineers each
- Focus areas: underwriting AI, policy management, claims processing, integrations, mobile apps, analytics platform

The security team is capable but overwhelmed. They're simultaneously implementing SOC 2 controls, preparing for state insurance examinations, and trying to remediate years of technical debt. The platform team is skilled but stretched thin supporting 130 product engineers across 6 AWS accounts.

## Post-Acquisition Remediation Requirements

A PE buyer should budget 18-24 months and significant capital investment for security remediation:

**Immediate (0-6 months, $500K-$750K):**
- Emergency IAM policy remediation - scope down wildcard permissions
- Close internet-exposed SSH and database ports
- Implement AWS Organizations with Service Control Policies
- Deploy centralized logging and monitoring across all accounts
- Rotate all service account credentials and API keys

**Medium-term (6-12 months, $1M-$1.5M):**
- Rebuild deployment pipeline with least-privilege IAM roles
- Implement proper secrets management patterns across all Lambda functions
- Deploy infrastructure-as-code with security guardrails
- Establish security baseline for all new AWS accounts
- Implement automated security scanning and compliance monitoring

**Long-term (12-24 months, $2M-$3M total security investment):**
- Complete SOC 2 Type II certification ($300K-$500K)
- Achieve state insurance security compliance in all 12 operating states
- Build mature security operations center with 24/7 monitoring
- Implement zero-trust architecture across all environments
- Hire 4-6 additional security engineers to support continued growth

The good news: InsureNet's core business metrics are strong, with 40% year-over-year revenue growth and 95% customer retention. Their product-market fit is solid. The security issues are remediable with proper investment and prioritization - they just need adult supervision and adequate funding.

**Risk Assessment:** Medium-High. The technical security debt is significant but not company-ending. Similar to many high-growth B2B SaaS companies that prioritized product velocity over security maturity. Remediation is expensive but achievable within 18-24 months with proper investment.