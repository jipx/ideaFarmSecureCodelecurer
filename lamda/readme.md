
## Lambda Functions Overview

The Secure Coding Grader system leverages four AWS Lambda functions to manage submission, grading, result retrieval, and dashboard functionality.

---

### 1. GetSignedUrlLambda

- **Purpose**: Generates a presigned S3 upload URL.
- **Trigger**: API Gateway (HTTP GET)
- **Logic**:
  - Creates a unique submission ID.
  - Returns a presigned URL for the student to upload their ZIP file securely to the source S3 bucket.

---

### 2. GraderLambdaFunction

- **Purpose**: Grades uploaded code asynchronously using a Bedrock Agent.
- **Trigger**: AWS SQS (event-driven)
- **Logic**:
  - Fetches and extracts the ZIP from S3.
  - Validates and analyzes the code (e.g., secure coding practices).
  - Invokes the Bedrock Agent with the code context.
  - Writes grading feedback to the report bucket and result metadata to DynamoDB.

---

### 3. GetResultLambda

- **Purpose**: Polls for grading results based on a submission ID.
- **Trigger**: API Gateway (HTTP GET)
- **Logic**:
  - Queries the DynamoDB table.
  - Returns grading results if completed; otherwise, reports in-progress status.

---

### 4. DashboardLambda

- **Purpose**: Lists all past grading results for display on a dashboard.
- **Trigger**: API Gateway (HTTP GET)
- **Logic**:
  - Scans the DynamoDB table.
  - Returns recent submissions and their grading metadata.

---

These Lambda functions form the backbone of the automated grading pipeline, enabling scalable and secure processing of code submissions in a serverless architecture.
