# CrediSure AWS Cloud Architecture

## Overview
This document describes the AWS deployment architecture for the CrediSure credit intelligence platform, covering security, scalability, monitoring, and backups.

## Architecture Components

### 1. Next.js Frontend Deployment
- **Service**: AWS Amplify or Amazon S3 + CloudFront
- **Why**: 
  - Amplify provides managed Next.js deployment with automatic CI/CD
  - S3 + CloudFront offers global CDN for fast static asset delivery
- **Configuration**:
  - Deploy frontend with environment variable `NEXT_PUBLIC_API_URL` pointing to the backend API domain
  - Enable HTTPS with AWS Certificate Manager (ACM)
  - Configure custom domain (e.g., app.credisure.ng)

### 2. FastAPI Backend Deployment
- **Service**: Amazon ECS (Elastic Container Service) with Fargate or AWS Elastic Beanstalk
- **Why**:
  - ECS Fargate provides serverless container orchestration for scalability
  - Auto-scaling groups adjust the number of containers based on traffic
- **Configuration**:
  - Dockerize the FastAPI application
  - Deploy to ECS with Application Load Balancer (ALB) for traffic routing
  - Use AWS IAM roles for ECS tasks to access other AWS services securely
  - Configure health checks on the ALB to ensure only healthy containers receive traffic

### 3. MySQL Database
- **Service**: Amazon RDS (Relational Database Service) for MySQL
- **Why**:
  - Managed MySQL database with automated backups and patches
  - Multi-AZ deployment for high availability
- **Configuration**:
  - Use db.t3.medium (or appropriate instance type)
  - Enable Multi-AZ for redundancy
  - Configure automatic backups with 7-day retention
  - Restrict access to the RDS instance using a VPC security group (only allow access from the backend ECS service)

### 4. Document Storage
- **Service**: Amazon S3 (Simple Storage Service)
- **Why**:
  - Scalable, durable object storage for bank statements and documents
  - Integrates with IAM for secure access control
- **Configuration**:
  - Create an S3 bucket (e.g., credisure-documents-production)
  - Enable server-side encryption (SSE-S3 or SSE-KMS)
  - Configure bucket policy to only allow access from the backend IAM role
  - Use S3 Versioning to keep previous versions of files

## Security Measures
1. **Network Security**:
   - Deploy all resources in a VPC (Virtual Private Cloud)
   - Use public and private subnets:
     - Public subnets: ALB, CloudFront
     - Private subnets: ECS tasks, RDS
   - Configure security groups to allow only necessary traffic (e.g., HTTPS to ALB, MySQL only from ECS)
2. **Authentication & Authorization**:
   - Use JWT tokens for API authentication (already implemented)
   - Use AWS IAM roles for service-to-service communication (no hardcoded credentials)
3. **Data Encryption**:
   - Encrypt data in transit using HTTPS (ACM certificates)
   - Encrypt data at rest (RDS encryption, S3 server-side encryption)
4. **Secrets Management**:
   - Store database credentials, API keys (GEMINI_API_KEY, etc.) in AWS Secrets Manager or AWS Systems Manager Parameter Store

## Scalability
1. **Frontend**:
   - CloudFront automatically scales to handle global traffic
   - Amplify supports automatic deployments and scaling
2. **Backend**:
   - ECS Service Auto Scaling: Adjust the number of Fargate tasks based on CPU/memory utilization or custom CloudWatch metrics
   - Application Load Balancer distributes traffic across multiple containers
3. **Database**:
   - RDS Read Replicas for read-heavy workloads (e.g., viewing past credit assessments)
   - Vertical scaling (change RDS instance type) if needed
4. **Storage**:
   - S3 automatically scales to any amount of data

## Monitoring
1. **AWS CloudWatch**:
   - Collect and track metrics (CPU, memory, request count, latency) for ECS, RDS, and ALB
   - Create CloudWatch Alarms to notify on high error rates or high CPU utilization
   - Store and view logs from ECS tasks and RDS in CloudWatch Logs
2. **X-Ray**:
   - Trace requests through the entire system to identify bottlenecks
3. **Third-party tools (optional)**:
   - New Relic, Datadog for enhanced monitoring and alerting

## Backups
1. **Database**:
   - RDS Automated Backups: Daily full backups with transaction logs for point-in-time recovery (PITR)
   - Manual DB Snapshots: Create before major changes
2. **Storage**:
   - S3 Versioning: Keep multiple versions of objects
   - S3 Cross-Region Replication (CRR): Replicate objects to another AWS region for disaster recovery
3. **Application Code**:
   - GitHub (already set up) for version control and source code backup

## Cost Optimization Tips
- Use AWS Free Tier for eligible services (RDS t2.micro, S3, ECS Fargate) when starting
- Use Spot Instances for non-critical workloads (if using ECS EC2 launch type)
- Set up S3 Lifecycle Policies to move old documents to cheaper storage tiers (S3 Glacier)
