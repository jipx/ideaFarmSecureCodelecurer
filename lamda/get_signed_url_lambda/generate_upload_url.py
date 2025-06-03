import boto3, json, os
from datetime import datetime

s3 = boto3.client('s3')
SOURCE_BUCKET = os.environ['SOURCE_BUCKET']

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        filename = body['filename']
        email = body.get('email', 'anonymous')

        key = f"{email}/{datetime.utcnow().isoformat()}_{filename}"
        signed_url = s3.generate_presigned_url('put_object', {
            'Bucket': SOURCE_BUCKET,
            'Key': key,
            'ContentType': 'application/zip'
        }, ExpiresIn=300)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "upload_url": signed_url,
                "s3_key": key
            }),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }