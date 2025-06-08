import json
import os
import boto3

dynamodb = boto3.resource("dynamodb")
s3 = boto3.client("s3")

def lambda_handler(event, context):
    print("Event received:", event)

    submission_id = event.get("queryStringParameters", {}).get("submission_id")
    if not submission_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing submission_id"})
        }

    table = dynamodb.Table(os.environ["TABLE_NAME"])
    try:
        response = table.get_item(Key={"submission_id": submission_id})
        item = response.get("Item")
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Database error: {str(e)}"})
        }

    if not item:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Result not found"})
        }

    report_key = item.get("report_key")
    print(f"Report key from DynamoDB: {report_key}")

    if not report_key:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Missing report_key in database"})
        }

    try:
        presigned_url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": os.environ["REPORT_BUCKET"],
                "Key": report_key
            },
            ExpiresIn=300
        )
        print(f"Presigned URL: {presigned_url}")
    except Exception as e:
        presigned_url = None
        print(f"Error generating signed URL: {str(e)}")

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
