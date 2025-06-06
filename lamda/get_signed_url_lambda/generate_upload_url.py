import boto3
import json
import os
from datetime import datetime
import os.path

s3 = boto3.client('s3')
SOURCE_BUCKET = os.environ['SOURCE_BUCKET']

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        filename = body.get('filename')
        student_id = body.get('student_id')
        action = body.get('action', 'put')  # 'put' or 'get'

        if not filename or not filename.endswith('.zip'):
            raise ValueError("Only .zip files are allowed")

        filename = os.path.basename(filename)

        # Try to extract email from Cognito claims
        email = None
        try:
            claims = event['requestContext']['authorizer']['claims']
            email = claims.get('email')
        except (KeyError, TypeError):
            pass

        # Use email > student_id > 'anonymous' as identifier
        identifier = email or student_id or 'anonymous'

        if action == 'put':
            timestamp = datetime.utcnow().isoformat()
            key = f"{identifier}/{timestamp}_{filename}"

            params = {
                'Bucket': SOURCE_BUCKET,
                'Key': key,
                'ContentType': 'application/zip',
                'Metadata': {
                    'submitted-by': identifier,
                    'filename': filename,
                    'timestamp': timestamp,
                    'assignment': 'secure-coding-report'
                }
            }

        elif action == 'get':
            key = f"{identifier}/{filename}"
            params = {
                'Bucket': SOURCE_BUCKET,
                'Key': key
            }

        else:
            raise ValueError("Action must be 'put' or 'get'")

        # Generate presigned URL
        signed_url = s3.generate_presigned_url(
            f"{action}_object",
            Params=params,
            ExpiresIn=300
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "url": signed_url,
                "s3_key": key
            }),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        }

    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": str(e)}),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            }
        }
