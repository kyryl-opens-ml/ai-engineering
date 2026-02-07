# DevPipe AWS Infrastructure Architecture

```mermaid
flowchart TB
    subgraph "VPC (10.0.0.0/16)"
        subgraph "EC2 Instances"
            EC2_1[devpipe-web-prod<br/>t3.large]
            EC2_2[devpipe-worker-01<br/>t3.medium]
            EC2_3[devpipe-jenkins<br/>t3.small]
        end

        subgraph "Security Groups"
            SG_1[devpipe-web-sg<br/>443,80 → 0.0.0.0/0]
            SG_2[devpipe-ssh-wide-open<br/>22 → 0.0.0.0/0]:::risk
            SG_3[devpipe-internal<br/>8080 → 10.0.0.0/16]
            SG_4[devpipe-database-sg<br/>5432 → 0.0.0.0/0]:::risk
        end
    end

    subgraph "IAM"
        subgraph "Roles"
            ROLE_1[DevPipeLambdaExecutionRole]:::risk
            ROLE_2[DevPipeEC2Role]
            ROLE_3[DevPipeLegacyAdminRole]:::risk
        end

        subgraph "Policies"
            POL_1[DevPipeComprehensivePolicy<br/>Action: *, Resource: *]:::risk
            POL_2[EC2BasicPolicy]
            POL_3[AdminAccessPolicy]:::risk
            POL_4[DeveloperPolicy]
        end

        subgraph "Users"
            USER_1[devpipe-deploy-user]:::risk
            USER_2[legacy-ci-user]:::risk
            USER_3[john-developer]
        end
    end

    subgraph "Lambda Functions"
        LAMBDA_1[devpipe-webhook-handler<br/>Python 3.8]:::risk
        LAMBDA_2[devpipe-build-processor<br/>Node.js 14.x]:::risk
        LAMBDA_3[devpipe-analytics<br/>Python 3.11]
    end

    subgraph "Storage"
        subgraph "S3 Buckets"
            S3_1[devpipe-builds<br/>Encrypted, Versioned]
            S3_2[devpipe-artifacts-public<br/>No encryption, Public]:::risk
            S3_3[devpipe-backups<br/>Encrypted, Versioned]
            S3_4[devpipe-logs<br/>Encrypted]
        end

        subgraph "DynamoDB Tables"
            DDB_1[devpipe-users<br/>Encrypted, PITR]
            DDB_2[devpipe-builds<br/>No encryption, No PITR]:::risk
            DDB_3[devpipe-analytics-events<br/>Encrypted]
        end
    end

    subgraph "Secrets & Messaging"
        subgraph "Secrets Manager"
            SEC_1[devpipe/prod/database<br/>DB credentials]
            SEC_2[devpipe/github-token<br/>No rotation]:::risk
            SEC_3[devpipe/api-keys<br/>Stripe keys]
        end

        subgraph "SQS Queues"
            SQS_1[devpipe-builds]
            SQS_2[devpipe-notifications]
            SQS_3[devpipe-analytics-dlq]
        end
    end

    %% Connections
    LAMBDA_1 --> DDB_2
    LAMBDA_1 --> SQS_1
    LAMBDA_2 --> S3_1
    LAMBDA_3 --> DDB_3

    ROLE_1 --> POL_1
    ROLE_2 --> POL_2
    ROLE_3 --> POL_3

    USER_1 --> POL_1
    USER_2 --> POL_3
    USER_3 --> POL_4

    EC2_1 --> SG_1
    EC2_2 --> SG_2
    EC2_3 --> SG_3

    classDef risk fill:#ff6b6b,stroke:#c92a2a,color:#fff
```

## Risk Summary

| Risk Category | Resource | Severity | Issue |
|---------------|----------|----------|-------|
| **IAM Overprivilege** | DevPipeComprehensivePolicy | 🔴 Critical | Wildcard permissions (*:*) |
| **IAM Overprivilege** | DevPipeLegacyAdminRole | 🔴 Critical | Cross-account trust with Principal: * |
| **IAM Overprivilege** | devpipe-database-sg | 🔴 Critical | Database port open to 0.0.0.0/0 |
| **IAM Overprivilege** | devpipe-ssh-wide-open | 🟠 High | SSH access from any IP |
| **Secrets Exposure** | devpipe-webhook-handler | 🟠 High | Plaintext credentials in Lambda env vars |
| **Secrets Exposure** | devpipe/github-token | 🟡 Medium | No automatic rotation configured |
| **Outdated Stack** | devpipe-webhook-handler | 🟠 High | Python 3.8 (EOL runtime) |
| **Outdated Stack** | devpipe-build-processor | 🟡 Medium | Node.js 14.x (deprecated) |

### Key Architectural Concerns

1. **Excessive Permissions**: Core Lambda execution role has administrative privileges across entire AWS environment
2. **Network Security**: Critical services exposed to internet without IP restrictions
3. **Data Protection**: Mixed encryption posture with some resources unprotected
4. **Legacy Debt**: Outdated runtimes and unused admin roles from acquisition integration
5. **Secrets Management**: Inconsistent use of Secrets Manager vs environment variables

### Business Impact
- **Compliance Risk**: Current setup violates SOC 2 requirements for enterprise customers
- **Blast Radius**: Overprivileged roles could amplify security incident impact
- **Operational Risk**: EOL runtimes may face unexpected deprecation by AWS