# ☁️ Secure Coding Grader - Full Stack Deployment (Lambda, S3, SQS, DDB, API Gateway, Bedrock)

This CloudFormation stack deploys a secure and scalable system for grading source code submissions using AWS services. It integrates Lambda functions, S3, SQS, DynamoDB, and API Gateway to form a serverless backend, with optional integration to AWS Bedrock Agents.

---

## 📦 Stack Components

| Resource Type       | Purpose                                                                 |
|---------------------|-------------------------------------------------------------------------|
| S3 Buckets          | Store uploaded ZIPs and generated grading reports                       |
| SQS Queue           | Decouples submission events from grading logic                          |
| DynamoDB Table      | Tracks grading progress and results using `submission_id`               |
| Lambda Functions    | Handle grading, upload URL generation, status polling, and dashboarding |
| API Gateway         | Exposes public HTTP endpoints for frontend (e.g., Streamlit app)        |
| IAM Roles & Policies| Secure Lambda access to required services                               |

---

## 🚀 Deployment Instructions

### 1. Package Lambda Code
Each Lambda (e.g. `grading_lambda/`, `get_result_lambda/`) should be zipped and uploaded to the designated S3 bucket (default: `ideafarm-lambda-assets`).

Example:
```bash
zip -r grading_lambda.zip grading_lambda/
aws s3 cp grading_lambda.zip s3://ideafarm-lambda-assets/
```

Ensure the following Lambda ZIPs are in your bucket:
- `grading_lambda.zip`
- `generate_upload_url.zip`
- `get_result_lambda.zip`
- `dashboard_lambda.zip`

### 2. Deploy the Stack
```bash
aws cloudformation deploy \
  --template-file secure-grader.yaml \
  --stack-name SecureCodingGrader \
  --capabilities CAPABILITY_NAMED_IAM \
  --parameter-overrides \
    AgentId=<YOUR_AGENT_ID> \
    AgentAliasId=<YOUR_AGENT_ALIAS_ID>
```

---

## 🌐 API Endpoints

| Purpose         | URL Format                                                                 |
|-----------------|-----------------------------------------------------------------------------|
| Get Upload URL  | `GET /get-signed-url`                                                      |
| Poll Grading    | `GET /poll?submission_id=<your-id>`                                       |
| Dashboard View  | `GET /dashboard`                                                           |

Example request:
```bash
curl "https://<rest_api_id>.execute-api.<region>.amazonaws.com/prod/get-signed-url"
```

---

## 🧠 How It Works

1. **Upload Phase**
   - Frontend calls `/get-signed-url` to obtain a presigned S3 URL
   - Uploads ZIP to S3 using the URL

2. **Processing Phase**
   - S3 triggers a message to the SQS queue
   - Grader Lambda pulls and processes the message
   - Invokes Bedrock Agent (if configured)
   - Stores results in DynamoDB and S3 report bucket

3. **Polling Phase**
   - Frontend queries `/poll?submission_id=xxx`
   - Returns status and report if ready

---

## 📁 Output Summary

| Output Name         | Description                               |
|---------------------|-------------------------------------------|
| `SignedUrlApi`      | Endpoint to get a signed upload URL       |
| `PollApi`           | Endpoint to check grading result          |
| `DashboardApi`      | Endpoint to list all reports              |
| `SourceBucket`      | Bucket for uploaded code ZIPs             |
| `ReportBucket`      | Bucket for generated grading reports      |
| `SQSQueue`          | Name of the submission queue              |
| `DynamoDBTable`     | Table tracking grading submissions        |
| `GraderLambdaName`  | Name of the grading handler Lambda        |

---

## 🛡️ Security & Best Practices

- Fine-grained IAM permissions for Lambda
- Use `PayPerRequest` for DynamoDB to optimize cost
- Tagging for resource identification
- Can add DLQ to SQS and timeout handling to Lambda for robustness

---

## 🛠️ Customization

To modify parameters like bucket names or table name:
```bash
aws cloudformation deploy --parameter-overrides \
  SourceBucketName=my-submissions \
  ReportBucketName=my-reports \
  TableName=myGradingTable \
  ...
```

---

## 🧾 License
This project is developed for educational and research purposes.
