
# Lambda Testing - Secure Code Grader

This test verifies that the `GraderLambdaFunction` processes a ZIP file submission correctly and invokes the Bedrock agent to generate grading feedback.

## Test File

- **File name**: `secure-code-submissions.zip`
- **S3 Bucket**: `secure-code-submissions`
- **Object Key**: `secure-code-submissions.zip`

## Expected Lambda Input

Triggered via SQS when the object is uploaded.

### Sample Event Payload
```json
{
  "Records": [
    {
      "messageId": "test-message-id",
      "receiptHandle": "test-receipt-handle",
      "body": "{\"submission_id\": \"abc123\", \"s3_key\": \"secure-submission.zip\"}",
      "attributes": {},
      "messageAttributes": {},
      "md5OfBody": "",
      "eventSource": "aws:sqs",
      "eventSourceARN": "arn:aws:sqs:ap-southeast-1:123456789012:SecureCodeSubmissionQueue",
      "awsRegion": "ap-southeast-1"
    }
  ]
}
```

## Expected Output

- Lambda invokes the Bedrock Agent with a JSON prompt.
- Receives a structured JSON feedback from the agent.
- Stores the result in the DynamoDB table `GradingSubmissions`.
- Uploads a report file to the S3 bucket `secure-code-reports`.

## Verification Steps

1. Check logs in CloudWatch to confirm the agent was invoked.
2. Validate the item in DynamoDB using `submission_id`.
3. Verify that the report file exists in `secure-code-reports/`.

