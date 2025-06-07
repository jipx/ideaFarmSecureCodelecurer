
# 📄 Presigned URL Generator for Secure Coding Submissions

This AWS Lambda function generates **short-lived presigned S3 URLs** to securely upload or download `.zip` files. It's designed for submitting secure coding reports or source code files, with optional Cognito integration for authenticated submissions.

---

## ✅ Features

- 🔐 Secure uploads/downloads via presigned S3 URLs (expires in 5 minutes)
- 📁 File structure: `student_id_or_email/timestamp_filename.zip`
- 🏷️ Metadata tags on upload: `submitted-by`, `filename`, `timestamp`, `assignment`
- 🧾 Supports both `PUT` (upload) and `GET` (download)
- 🛡️ Extracts email from Cognito claims if available

---

## 🛠️ Deployment Requirements

- Python 3.11+ Lambda runtime
- API Gateway (REST or HTTP)
- S3 bucket for storage
- Optional: Cognito User Pool with hosted UI for token-based access

---

## ⚙️ Environment Variables

| Name           | Description                     |
|----------------|---------------------------------|
| `SOURCE_BUCKET`| Name of your S3 bucket          |

---

## 🚀 API Endpoint

### POST `/generate-url`

**Request Body (JSON)**

```
{
  "filename": "report.zip",
  "student_id": "S1234567A",  // optional if using Cognito
  "action": "put"             // or "get"
}
```

**Authorization Header (optional)**

```
Authorization: Bearer <id_token_from_cognito>
```

**Successful Response (200)**

```
{
  "url": "https://your-bucket.s3.amazonaws.com/...",
  "s3_key": "S1234567A/2025-06-06T13:45:10Z_report.zip"
}
```

---

## 🧪 Local Unit Testing

Install dependencies:

```bash
pip install pytest moto boto3
```

Run tests:

```bash
pytest test_lambda.py
```

Example test cases:

- PUT with student ID
- GET with Cognito email
- Invalid actions and file types

---

## 🌐 Postman Testing

1. Use the provided `cognito_presigned_upload.postman_collection.json`
2. Steps:
   - Exchange Cognito authorization code for `id_token`
   - Use `id_token` to request a presigned URL from the API Gateway endpoint
3. Replace placeholders (`<client_id>`, `<domain>`, etc.) before use

---

## 🧾 S3 Object Metadata

| Key           | Description                      |
|---------------|----------------------------------|
| `submitted-by`| Student ID or Cognito email      |
| `filename`    | Name of the uploaded file        |
| `timestamp`   | UTC timestamp at upload time     |
| `assignment`  | Fixed label (e.g., secure-coding-report) |

---

## 🛡️ IAM Policy Example for Lambda

```json
{
  "Effect": "Allow",
  "Action": ["s3:PutObject", "s3:GetObject"],
  "Resource": "arn:aws:s3:::your-bucket-name/*"
}
```

---

## 📁 Sample Project Structure

```
project/
├── lambda_function.py
├── test_lambda.py
├── .gitignore
├── README.md
└── frontend/
    └── .streamlit/secrets.toml  # ignored
```

---

## 🛠 To-Do

- [ ] Add DynamoDB logging
- [ ] Add API Gateway token validation
- [ ] Add expiration notifications via SNS
