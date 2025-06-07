# Secure Coding Grader Project# 🔐 Secure Coding Grader System

This project provides a fully serverless, scalable platform to automate the grading of student secure code submissions using AWS Bedrock, Lambda, and Streamlit.

---
https://jipx.github.io/ideaFarmSecureCodelecurer/Documentation/Eventbridge.html
## 📦 Features

- 📤 Secure upload of student code ZIP files via signed S3 URLs
- 📬 Automatic grading via Lambda triggered through SQS
- 🧠 Bedrock integration to analyze code and generate feedback
- 📊 Instructor dashboard for monitoring grading status
- 📁 Separate S3 buckets for source submissions and reports
- 📑 Editable grading rules and policy configurations
- 🔁 Polling API to check grading completion

---

## 🚀 Deployment

### 1. Upload Lambda Artifacts
Use the script below to upload all zipped Lambda functions and template to your deployment bucket.

```bash
chmod +x deploy.sh
./deploy.sh
```

**Make sure to update** `your-deployment-bucket-name` in `deploy.sh`.

### 2. Deploy CloudFormation

This provisions:
- S3 buckets (`submissions`, `reports`)
- SQS Queue
- DynamoDB table
- 5 Lambda functions
- 3 API Gateway endpoints

**CloudFormation template**: [`secure_code_grader_complete.yaml`](infra/secure_code_grader_complete.yaml)

---

## 🔗 API Endpoints

| Function | Path | Method |
|---------|------|--------|
| Upload URL | `/get-signed-url` | `POST` |
| Poll Status | `/poll` | `GET` |
| Dashboard View | `/dashboard` | `GET` |

---

## 🧪 Frontend Pages (Streamlit)

| Page | Purpose |
|------|---------|
| 📤 Upload Submission | Upload student ZIPs and poll status |
| 📊 Grading Dashboard | View score, status, and download reports |

---

## 📝 Notes

- Lambda functions must be zipped and uploaded to the specified S3 bucket prior to stack launch
- You can modify grading logic in `grader_lambda_with_result_storage.py`
- Bedrock model permissions must be granted to the Lambda execution role

---

Project sponsored by **Ideafarm @ Singapore Polytechnic**