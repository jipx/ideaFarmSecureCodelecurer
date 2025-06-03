import boto3, json, os
from boto3.dynamodb.conditions import Key

ddb = boto3.resource('dynamodb')
TABLE_NAME = os.environ['DDB_TABLE']

def lambda_handler(event, context):
    table = ddb.Table(TABLE_NAME)
    try:
        params = json.loads(event.get('body', '{}'))
        email = params.get('email')

        if email:
            resp = table.query(
                IndexName='email-index',
                KeyConditionExpression=Key('email').eq(email)
            )
        else:
            resp = table.scan(Limit=100)

        items = resp.get('Items', [])
        return {
            "statusCode": 200,
            "body": json.dumps([
                {
                    "submission_id": i['submission_id'],
                    "email": i.get('email'),
                    "timestamp": i.get('timestamp'),
                    "report_key": i.get('report_key'),
                    "feedback_summary": i.get('feedback_summary', '')
                } for i in items
            ]),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
            "headers": {"Access-Control-Allow-Origin": "*"}
        }