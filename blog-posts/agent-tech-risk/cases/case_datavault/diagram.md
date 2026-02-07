# DataVault Infrastructure Architecture

```mermaid
flowchart TB
    subgraph "AWS Account - Production"
        subgraph "VPC - 10.0.0.0/16"
            subgraph "Compute Layer"
                EC2_API["EC2: datavault-prod-api-01<br/>t3.large"]
                EC2_WORKER["EC2: datavault-prod-worker-01<br/>t3.xlarge"]
                EC2_MONITOR["EC2: datavault-monitoring<br/>t3.small"]
            end

            subgraph "Serverless Layer"
                LAMBDA_AUTH["Lambda: datavault-user-auth<br/>Python 3.11"]:::risk
                LAMBDA_PROCESS["Lambda: datavault-data-processor<br/>Python 3.9"]
                LAMBDA_WEBHOOK["Lambda: datavault-webhook-handler<br/>Node.js 18"]:::risk
                LAMBDA_REPORT["Lambda: datavault-report-generator<br/>Python 3.11"]
            end

            subgraph "Security Groups"
                SG_WEB["datavault-web-sg<br/>HTTPS/HTTP from 0.0.0.0/0"]
                SG_ADMIN["datavault-admin-sg<br/>SSH/RDP from 0.0.0.0/0"]:::risk
                SG_DB["datavault-db-sg<br/>PostgreSQL from VPC"]
                SG_K8S["datavault-k8s-sg<br/>K8s API from VPC"]
            end
        end

        subgraph "Storage Layer"
            S3_CUSTOMER["S3: datavault-prod-customer-data<br/>No Encryption, No Versioning"]:::risk
            S3_BACKUP["S3: datavault-backup-archives<br/>Encrypted, Versioned"]
            S3_STATIC["S3: datavault-static-assets<br/>Public Access Enabled"]:::risk
            S3_LOGS["S3: datavault-logs-central<br/>Encrypted, Versioned"]
        end

        subgraph "Database Layer"
            DDB_SESSIONS["DynamoDB: datavault-user-sessions<br/>No Encryption, No PITR"]:::risk
            DDB_CUSTOMER["DynamoDB: datavault-customer-data<br/>No Encryption, No PITR"]:::risk
            DDB_AUDIT["DynamoDB: datavault-audit-logs<br/>Encrypted, PITR Enabled"]
            DDB_CACHE["DynamoDB: datavault-analytics-cache<br/>Encrypted, No PITR"]
        end

        subgraph "Queue Layer"
            SQS_PROC["SQS: datavault-processing-queue"]
            SQS_NOTIF["SQS: datavault-notifications"]
            SQS_DLQ["SQS: datavault-dlq"]
        end

        subgraph "Secrets Management"
            SECRET_DB["SecretsManager: datavault/prod/database<br/>No Rotation"]:::risk
            SECRET_API["SecretsManager: datavault/prod/third-party-apis<br/>No Rotation"]:::risk
            SECRET_LEGACY["SecretsManager: datavault/legacy/old-db-creds<br/>Plaintext Format"]:::risk
        end

        subgraph "IAM Layer"
            ROLE_LAMBDA["Role: DataVaultLambdaExecutionRole"]
            ROLE_EC2["Role: DataVaultEC2Role"]
            ROLE_K8S["Role: DataVaultK8sServiceRole"]
            USER_CI["User: datavault-ci-deploy"]
            USER_ANALYTICS["User: datavault-analytics"]
        end
    end

    subgraph "Staging Environment"
        VPC_STAGING["VPC: datavault-staging-vpc<br/>10.1.0.0/16"]
        EC2_STAGING["EC2: datavault-staging-web<br/>t3.medium"]
    end

    %% Connections
    LAMBDA_AUTH --> SECRET_DB
    LAMBDA_AUTH --> DDB_SESSIONS
    LAMBDA_WEBHOOK --> SECRET_API
    LAMBDA_PROCESS --> S3_CUSTOMER
    LAMBDA_PROCESS --> DDB_CUSTOMER
    LAMBDA_REPORT --> S3_BACKUP

    EC2_API --> DDB_CUSTOMER
    EC2_API --> S3_CUSTOMER
    EC2_WORKER --> SQS_PROC
    EC2_WORKER --> DDB_CACHE

    SG_ADMIN --> EC2_API
    SG_ADMIN --> EC2_WORKER
    SG_WEB --> EC2_API

    %% Risk styling
    classDef risk fill:#ff6b6b,stroke:#c92a2a,color:#fff
```

## Risk Summary

| **Risk Category** | **Resource** | **Severity** | **Issue** |
|-------------------|--------------|--------------|-----------|
| **Secrets Exposure (tr2)** | datavault-user-auth | Critical | DB password, JWT secret, API key in plaintext env vars |
| **Secrets Exposure (tr2)** | datavault-webhook-handler | High | Stripe secrets exposed in Lambda environment |
| **Secrets Exposure (tr2)** | datavault/prod/database | Medium | SecretsManager without rotation enabled |
| **Secrets Exposure (tr2)** | datavault/legacy/old-db-creds | Medium | Legacy credentials in plaintext format |
| **Storage Misconfiguration (tr3)** | datavault-prod-customer-data | Critical | No encryption, versioning suspended |
| **Storage Misconfiguration (tr3)** | datavault-static-assets | High | Public access permissions enabled |
| **Storage Misconfiguration (tr3)** | datavault-user-sessions | High | DynamoDB table lacks encryption |
| **Storage Misconfiguration (tr3)** | datavault-customer-data | High | No encryption, no point-in-time recovery |
| **Low SLA (tr9)** | datavault-prod-customer-data | High | Versioning suspended, no backup protection |
| **Low SLA (tr9)** | datavault-user-sessions | Medium | No point-in-time recovery backup |
| **Low SLA (tr9)** | datavault-customer-data | High | No PITR backup protection |

## Architecture Notes

- **Production VPC**: Core infrastructure isolated in 10.0.0.0/16 network
- **Multi-tier Architecture**: Web, application, and data layers with appropriate security groups
- **Serverless Integration**: Lambda functions handle authentication, webhooks, and data processing
- **Storage Strategy**: Mix of S3 and DynamoDB with inconsistent encryption and backup policies
- **Access Control**: IAM roles and policies with some overly permissive configurations
- **Monitoring**: Dedicated monitoring instance but limited security observability