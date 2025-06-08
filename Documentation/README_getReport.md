# 🧠 Secure Grading App (Streamlit + AWS)

A serverless Streamlit application to check grading status and download reports securely. Built on AWS Lambda, S3, API Gateway, DynamoDB, and EventBridge. Designed for both students and admin staff.

---

## 🚀 Features

### 👩‍🎓 Student
- Upload code submission (ZIP)
- Check grading status
- Download report via signed S3 URL (expires in 10 minutes)

### 👨‍🏫 Admin
- View all submissions via Streamlit
- Filter by status (completed, pending, error)
- Export results to CSV
- View and download individual reports

---

## 🧱 Architecture Overview

```
[Streamlit UI]
  ├── Upload to S3 (presigned)
  ├── /status → API Gateway → Lambda → DynamoDB
  └── /signed-url → API Gateway → Lambda → S3 signed URL

[S3 (secure-code-submissions)]
  └── triggers → Grading Lambda
        ├── Grades and saves to DynamoDB
        ├── Writes report to secure-code-reports bucket
        └── Emits EventBridge event

[EventBridge]
  └── triggers → Notify Lambda → (optional SNS/email)
```

📎 Architecture diagram (edit in draw.io):  
🔗 [Download secure_grading_architecture.drawio](secure_grading_architecture.drawio)

---

## 📦 AWS Services

| Service       | Role                              |
|---------------|-----------------------------------|
| S3            | Stores uploaded ZIPs and reports  |
| Lambda        | Processes grading, status, and URLs |
| DynamoDB      | Stores metadata and statuses      |
| API Gateway   | Provides public `/status` and `/signed-url` endpoints |
| EventBridge   | Triggers notifications            |
| SNS (optional)| Sends notification emails         |

---

## 🔧 API Endpoints

### GET `/status?submission_id=sub-123`
Returns grading status and report key.

### GET `/signed-url?key=reports/sub-123.pdf`
Returns a 10-min signed S3 download link.

---

## 🧾 DynamoDB Structure

```json
{
  "submission_id": "sub-abc123",
  "email": "student@example.com",
  "status": "completed",
  "report_key": "reports/sub-abc123.pdf",
  "updated_at": "2025-06-07T08:30:00Z"
}
```

---

## 🖥️ Streamlit App Structure

```
streamlit-app/
├── app.py
├── pages/
│   ├── status_checker.py   # Student page
│   └── admin_dashboard.py  # Admin page
├── lambda_get_status.py
├── lambda_get_signed_url.py
├── cloudformation.yaml
├── requirements.txt
└── README.md
```

---

## 🔐 IAM Policy Snippet

```json
{
  "Action": [
    "dynamodb:GetItem",
    "dynamodb:Scan",
    "s3:GetObject"
  ],
  "Effect": "Allow",
  "Resource": "*"
}
```

---

## 🛠️ Setup

1. Deploy backend with `cloudformation.yaml`
2. Provide credentials in `~/.streamlit/secrets.toml`:
```toml
AWS_ACCESS_KEY_ID = "..."
AWS_SECRET_ACCESS_KEY = "..."
AWS_DEFAULT_REGION = "ap-southeast-1"
```
3. Run app:
```bash
streamlit run app.py
```

---

## 📬 Postman & OpenAPI

Postman Collection: [Download](https://gist.githubusercontent.com/jipx/abcd1234/raw/GradingStatusAPI.postman_collection.json)  
OpenAPI Spec included in this repo (future enhancement)


---

## 🧠 Lambda Functions

### 1. `lambda_get_status.py`
Triggered by API Gateway `/status`:
- Reads `submission_id` from query string
- Looks up DynamoDB table `GradingSubmissions`
- Returns grading status and report key in JSON

### 2. `lambda_get_signed_url.py`
Triggered by API Gateway `/signed-url`:
- Accepts `key` (S3 object key) from query string
- Returns a signed URL for downloading report (valid for 10 minutes)

### 3. `lambda_grading_handler.py`
Triggered by S3 upload or SQS (future):
- Unzips student submission
- Runs grading logic (e.g., lint, CodeQL, or Bedrock)
- Saves PDF report to `secure-code-reports` bucket
- Updates DynamoDB with status and report path
- Emits EventBridge event

### 4. `lambda_notify_complete.py`
Triggered by EventBridge:
- Sends SNS/email or logs status
- Optionally writes JSON to `status/` path in S3


---

## 🧑‍🏫 License

MIT License – Educational use only.  
Built for secure, serverless assessment automation.


---

## 🧾 Lambda Function Source Code
### `lambda_get_signed_url.py`
```python
import boto3
import json
import os

s3 = boto3.client("s3")
BUCKET_NAME = os.environ["REPORT_BUCKET"]

def lambda_handler(event, context):
    key = event.get("queryStringParameters", {}).get("key")
    if not key:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing key"})}

    try:
        signed_url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": BUCKET_NAME, "Key": key},
            ExpiresIn=600
        )
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"signed_url": signed_url})
        }
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}
```
### `lambda_get_status.py`
```python
import boto3
import json
import os

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["DDB_TABLE"])

def lambda_handler(event, context):
    submission_id = event.get("queryStringParameters", {}).get("submission_id")
    if not submission_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Missing submission_id"})}

    response = table.get_item(Key={"submission_id": submission_id})
    item = response.get("Item")
    if not item:
        return {"statusCode": 404, "body": json.dumps({"error": "Submission not found"})}

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json", "Access-Control-Allow-Origin": "*"},
        "body": json.dumps({
            "submission_id": item["submission_id"],
            "status": item["status"],
            "report_key": item.get("report_key"),
            "updated_at": item.get("updated_at")
        })
    }
```
