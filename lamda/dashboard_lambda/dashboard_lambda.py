# need to returnin gsigned url after retriving from dynamodb

import json
import boto3

dynamodb = boto3.resource('dynamodb')
TABLE_NAME = 'GradingSubmissions'  # Update if your table name differs
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        response = table.scan()
        items = response.get('Items', [])

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(items)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }
