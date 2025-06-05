
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


In AWS Lambda, "deploy" and "publish" refer to different but related concepts:

🔧 1. Deploy
Deploy means updating the function code or configuration, typically the $LATEST version.

When you edit code in the AWS Console or upload a new deployment package (via AWS CLI, SAM, CDK, etc.), you are deploying the changes to the $LATEST version.

This version is mutable — changes immediately overwrite the previous code/config in $LATEST.

🟡 Deploy = "Push updates to $LATEST"

📌 2. Publish
Publish means creating an immutable snapshot of the current $LATEST version.

When you publish, AWS creates a new version number (e.g., 1, 2, 3, etc.).

That version is read-only — code and configuration are frozen.

This is useful for production stability and safe rollbacks.

🟢 Publish = "Create a fixed version from $LATEST"

🧠 Summary
Operation	What It Does	Target	Mutable?	Use Case
Deploy	Updates code/config	$LATEST	✅ Yes	Iteration, testing
Publish	Freezes $LATEST into version	1, 2, 3...	❌ No	Production, rollback, version control

🏷️ Bonus: Aliases
You can use aliases to point to a published version:

prod → version 5

dev → $LATEST

This lets you safely route traffic or perform blue/green deployments.