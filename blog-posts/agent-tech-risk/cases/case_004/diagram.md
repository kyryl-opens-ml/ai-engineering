# CloudSync AWS Infrastructure Diagram

## Architecture Overview

```mermaid
flowchart TB
    subgraph Internet
        Users[Users/Clients]
        Legacy[Legacy Desktop Clients v1.x]
    end

    subgraph VPC["VPC: 10.0.0.0/16"]
        subgraph Public["Public Subnets (10.0.1-3.0/24)"]
            ALB[Application Load Balancer]
            NAT[NAT Gateway]
            LegacyASG["Legacy API ASG<br/>t2.micro x2<br/>min=max=2"]:::risk
        end

        subgraph Private["Private Subnets (10.0.10-12.0/24)"]
            subgraph EKS["EKS Cluster: cloudsync-prod<br/>K8s v1.25"]:::risk
                Workers["Worker Nodes<br/>m5.xlarge x3<br/>min=max=3"]:::risk
                GPU["GPU Nodes<br/>g4dn.xlarge x2"]
                Pods[Microservices Pods]
            end

            RDS["RDS PostgreSQL<br/>db.t2.micro<br/>Single-AZ<br/>No Performance Insights"]:::risk
            RDSAnalytics["RDS Analytics<br/>db.r5.xlarge<br/>Multi-AZ"]
            Redis[ElastiCache Redis<br/>cache.r5.large]
        end
    end

    subgraph Lambda["Lambda Functions"]
        WebhookLambda["Webhook Handler<br/>Python 3.8 EOL<br/>512MB<br/>Pool Size=5"]:::risk
        FileLambda["File Processor<br/>Python 3.11<br/>128MB<br/>No Concurrency Limit"]:::risk
        APIGateway["API Gateway<br/>Node.js 18<br/>1024MB"]
        NightlyLambda["Nightly Aggregation<br/>Python 3.12<br/>3008MB"]
    end

    subgraph S3["S3 Buckets"]
        ProdData[cloudsync-prod-data<br/>2.8TB]
        Backups[cloudsync-backups<br/>5.4TB]
        Processing[cloudsync-data-processing<br/>156GB]
        Logs[cloudsync-logs<br/>892GB]
    end

    subgraph IAM["IAM & Access"]
        EKSRole[EKS Cluster Role]
        NodeRole[EKS Node Role]
        LambdaRole[Lambda Execution Role]
        PublicEKS["EKS API: Public Access<br/>0.0.0.0/0"]:::risk
    end

    subgraph Monitoring["CloudWatch Monitoring"]
        RDSAlarm[RDS CPU > 80%<br/>State: OK]
        LambdaAlarm["File Processor Errors<br/>State: ALARM"]:::risk
        EKSAlarm[EKS Node CPU > 85%<br/>State: OK]
    end

    %% User connections
    Users --> ALB
    Legacy --> LegacyASG
    Users --> APIGateway

    %% Load balancer to services
    ALB --> Pods
    ALB --> LegacyASG

    %% EKS connections
    EKSRole -.->|manages| EKS
    NodeRole -.->|used by| Workers
    NodeRole -.->|used by| GPU
    PublicEKS -.->|exposes| EKS

    %% Lambda connections
    WebhookLambda --> RDS
    WebhookLambda --> Redis
    FileLambda --> Processing
    APIGateway --> RDS
    APIGateway --> Redis
    NightlyLambda --> RDSAnalytics
    NightlyLambda --> S3

    %% Service to database
    Pods --> RDS
    Pods --> Redis
    LegacyASG --> RDS
    LegacyASG --> Redis

    %% Data connections
    Pods --> ProdData
    Pods --> Processing
    LegacyASG --> ProdData
    RDS -.->|replicated to| RDSAnalytics

    %% Monitoring
    RDSAlarm -.->|monitors| RDS
    LambdaAlarm -.->|monitors| FileLambda
    EKSAlarm -.->|monitors| Workers

    %% Backups
    RDS -.->|backups| Backups
    RDSAnalytics -.->|backups| Backups

    %% Styling
    classDef risk fill:#ff6b6b,stroke:#c92a2a,color:#fff,stroke-width:3px
    classDef normal fill:#4dabf7,stroke:#1971c2,color:#fff
    classDef storage fill:#51cf66,stroke:#2f9e44,color:#fff

    class ProdData,Backups,Processing,Logs storage
```

## Risk Summary Table

| Risk ID | Category | Resource | Severity | Issue |
|---------|----------|----------|----------|-------|
| R1 | tr6 | `legacy-api-asg` | HIGH | Auto Scaling Group with min=max=2, no autoscaling capability |
| R2 | tr6 | `cloudsync-webhook-handler` | MEDIUM | Hardcoded DB_POOL_SIZE=5 preventing connection scaling |
| R3 | tr6 | `cloudsync-prod-workers` | HIGH | EKS node group with min=max=3, no horizontal scaling |
| R4 | tr8 | `cloudsync-prod-db` | CRITICAL | Production database on db.t2.micro, severely under-provisioned |
| R5 | tr8 | `cloudsync-file-processor` | HIGH | Lambda with 128MB memory processing 100MB files, frequent timeouts |
| R6 | tr8 | `legacy-api-worker-1/2` | HIGH | Production API on t2.micro instances |
| R7 | tr13 | `cloudsync-webhook-handler` | HIGH | Python 3.8 runtime (EOL October 2024) |
| R8 | tr13 | `cloudsync-prod` EKS | HIGH | Kubernetes 1.25 (4 versions behind, extended support ends April 2026) |
| R9 | tr13 | `legacy-api-worker-1/2` | MEDIUM | Ubuntu 18.04 AMI (EOL May 2023) |
| R10 | tr6 | `cloudsync-prod` EKS API | MEDIUM | Public access enabled with 0.0.0.0/0 CIDR |
| R11 | tr8 | `cloudsync-prod-db` | HIGH | No Multi-AZ deployment (single point of failure) |
| R12 | tr8 | `cloudsync-prod-db` | MEDIUM | Performance Insights disabled, no detailed monitoring |
| R13 | tr6 | `cloudsync-file-processor` | MEDIUM | No reserved concurrency limit (can exhaust account limits) |

## Architecture Notes

### Scaling Bottlenecks
- **Legacy API ASG**: Fixed at 2 instances, cannot scale for traffic spikes
- **EKS Workers**: Fixed at 3 nodes, limits Kubernetes pod scaling at 75% capacity
- **Main Database**: t2.micro with burstable performance, CPU credits exhausted during peak hours

### End-of-Life Components
- **Python 3.8**: Webhook handler on unsupported runtime
- **Kubernetes 1.25**: 4 versions behind, approaching end of extended support
- **Ubuntu 18.04**: Legacy API servers on EOL operating system

### Capacity Concerns
- **Database**: t2.micro handling production load through aggressive caching
- **Lambda Memory**: File processor undersized for actual workload (video, PDF processing)
- **No Multi-AZ**: Database failure means full outage (no failover)

### Configuration Risks
- **Hardcoded Limits**: Database pool size prevents Lambda scaling
- **Public EKS Access**: API server exposed to internet with wide CIDR
- **Unlimited Lambda Concurrency**: File processor can consume all account concurrency

### Monitoring Gaps
- **Performance Insights**: Disabled on production database
- **File Processor**: Currently in ALARM state (high error rate)
- **No Autoscaling Metrics**: Static groups have no scaling triggers configured
