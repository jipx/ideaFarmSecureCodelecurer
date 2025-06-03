import boto3, json, os, zipfile, io
from datetime import datetime

s3 = boto3.client('s3')
ddb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-agent-runtime')

SOURCE_BUCKET = os.environ['SOURCE_BUCKET']
REPORT_BUCKET = os.environ['REPORT_BUCKET']
TABLE_NAME = os.environ['DDB_TABLE']
AGENT_ID = os.environ['AGENT_ID']
AGENT_ALIAS_ID = os.environ['AGENT_ALIAS_ID']

def lambda_handler(event, context):
    for record in event['Records']:
        try:
            message = json.loads(record['body'])
            s3_key = message['s3_key']
            email = message.get('email', 'unknown')
            submission_id = message.get('submission_id', f"sub-{datetime.utcnow().isoformat()}")

            zip_obj = s3.get_object(Bucket=SOURCE_BUCKET, Key=s3_key)
            zip_data = zip_obj['Body'].read()

            with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                valid_files = [f for f in z.namelist() if f.endswith(('.py', '.js'))]
                if not valid_files:
                    raise ValueError("No valid source files")
                code = {f: z.read(f).decode('utf-8') for f in valid_files}

            prompt = {"input": {"source_code_files": code}}

            response = bedrock.invoke_agent(
                agentId=AGENT_ID,
                agentAliasId=AGENT_ALIAS_ID,
                sessionId=submission_id,
                inputText=json.dumps(prompt),
                )

            response_text = ""
            for event in response["completion"]:
                chunk = event.get("chunk", {}).get("bytes", b"")
                response_text += chunk.decode("utf-8")

            print("Response Text:", response_text)

            try:
                feedback = json.loads(response_text)
            except json.JSONDecodeError:
                feedback = {
                    "submission_id": submission_id,
                    "raw_feedback": response_text.strip()
                }
        
            
            print("Parsed feedback:", feedback)

            report_key = f"{submission_id}/grading_report.json"
            s3.put_object(Bucket=REPORT_BUCKET, Key=report_key, Body=json.dumps(feedback))

            ddb.Table(TABLE_NAME).put_item(Item={
                "submission_id": submission_id,
                "email": email,
                "timestamp": datetime.utcnow().isoformat(),
                "report_key": report_key,
                "feedback_summary": feedback.get("summary", "N/A")
            })

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            raise

    return {"status": "done"}