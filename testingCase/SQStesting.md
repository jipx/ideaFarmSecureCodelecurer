
## ✅ Test Case: SQS Trigger for Grader Lambda (`TC002`)

**Purpose:** Ensure that when the file `secure-code-submissions.zip` is uploaded to the `secure-code-submissions` S3 bucket, an SQS message is triggered and handled by the `GraderLambdaFunction`.

---

### 🧪 Steps

1. **Confirm Setup**
   - ✅ **S3 bucket:** `secure-code-submissions`
   - ✅ **SQS queue:** `SecureCodeSubmissionQueue`
   - ✅ **Lambda function:** `GraderLambdaFunction` is subscribed to the queue.

2. **Manually Send Test Message to SQS**

```bash
aws sqs send-message   --queue-url https://sqs.ap-northeast-1.amazonaws.com/628902727523/SecureCodeSubmissionQueue   --message-body '{\"submission_id\": \"abc123\", \"s3_key\": \"secure-submission.zip \"}'
```

in AWs Console: 
```bash
{
  "submission_id": "abc323",
  "s3_key": "secure-submission.zip"
}
```
3. **Verify Lambda Execution**
   - Check **CloudWatch Logs** for `GraderLambdaFunction`.
   - Confirm it processes the object `secure-code-submissions.zip`.

4. **Expected Output**
   - The Lambda:
     - Downloads the ZIP from S3
     - Runs grading logic
     - Stores grading result in the DynamoDB table `GradingSubmissions`

---

### ❌ Negative Test Case

Send an invalid SQS message like:

```json
{"invalid": "payload"}
```

✅ Expected: Lambda should log an error but **not crash**.
