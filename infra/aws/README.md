# AWS fallback (priority #2)

Use only when Meta-named partners (Meta Model API, Modal, Baseten, Fireworks) cannot cover a layer.

## Immediate AWS piece (recommended even in Modal-primary mode)

- **S3 bucket** `hypatia-media` in `ap-south-1` (or your region)
- IAM user/role with `s3:PutObject`, `s3:GetObject`, `s3:ListBucket`
- Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET` in Modal Secret `hypatia-secrets`

## If Modal is unavailable for the API

1. Build `services/api/Dockerfile` → push to ECR  
2. Run on **ECS Fargate** (CPU) behind an ALB  
3. Put Glimmer on **EC2 g5/g6** or **SageMaker** (Fargate has no GPU)  
4. Frontend on **Amplify** or S3+CloudFront  

Terraform/CDK scaffolding can be added once the Modal path is proven live.
