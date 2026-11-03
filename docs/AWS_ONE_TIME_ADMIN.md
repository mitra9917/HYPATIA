# One-time AWS admin step (required before `bash scripts/deploy_aws_api.sh`)

The local IAM user **`hypatia-cli`** cannot attach its own permissions. An **account admin** (root or IAM admin) must do this **once** in the AWS Console.

## 1. Attach deploy policy

1. Open [IAM → Users → hypatia-cli → Permissions](https://console.aws.amazon.com/iam/home#/users/details/hypatia-cli?section=permissions) (account `620694778016`).
2. **Add permissions** → **Create inline policy** → **JSON**.
3. Paste the contents of [`hypatia-deploy-policy.json`](./hypatia-deploy-policy.json) in this folder.
4. Name: **`HypatiaDeploy`**, save.

## 2. Verify from your laptop

```bash
aws sts get-caller-identity
aws ecr describe-repositories --region ap-south-1
```

The ECR command should succeed (empty list is OK).

## 3. Deploy API

```bash
cd /path/to/HYPATIA
bash scripts/deploy_aws_api.sh
```

Copy the printed **`HYPATIA_API_URL`**.

## 4. Vercel (Production)

Set on project **hypatia**:

| Variable | Value |
|----------|--------|
| `API_ORIGIN` | App Runner URL |
| `NEXT_PUBLIC_API_ORIGIN` | same |

Redeploy production. Turn off **Deployment Protection** on production so judges need no login.

## S3 note

If uploads still fail after deploy, add **`s3:PutObject` / `GetObject` / `ListBucket`** on bucket **`hypatias3mediauploader`** to the same policy (already included in `hypatia-deploy-policy.json`).
