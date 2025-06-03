import json
import os
import boto3

# Initialize AWS clients for DynamoDB and S3
dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

def lambda_handler(event, context):
    print("Event received:", event)

    # Extract submission_id from the query string parameters
    submission_id = event.get("queryStringParameters", {}).get("submission_id")
    if not submission_id:
        # Return a 400 error if submission_id is missing
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing submission_id"})
        }

    # Reference the DynamoDB table defined in environment variable
    table = dynamodb.Table(os.environ["TABLE_NAME"])
    try:
        # Retrieve item by submission_id from DynamoDB
        response = table.get_item(Key={"submission_id": submission_id})
        item = response.get("Item")
    except Exception as e:
        # Return a 500 error in case of DynamoDB failure
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Database error: {str(e)}"})
        }

    # If no item found, return 404
    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Result not found"})
        }

    # Generate a presigned URL for the report in the S3 bucket
    try:
        report_key = f"{submission_id}.txt"
        presigned_url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": os.environ["REPORT_BUCKET"],
                "Key": report_key
            },
            ExpiresIn=300  # URL expires in 5 minutes
        )
    except Exception as e:
        # In case URL generation fails, skip URL
        presigned_url = None

    # Return feedback and optionally the report URL
    return {
        "statusCode": 200,
        "body": json.dumps({
            "submission_id": submission_id,
            "feedback": item.get("feedback", "No feedback found."),
            "report_url": presigned_url
        }),
        "headers": {
            "Content-Type": "application/json"
        }
    }
