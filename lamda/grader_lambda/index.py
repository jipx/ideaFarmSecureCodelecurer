import boto3, json, os, zipfile, io
from datetime import datetime
from botocore.config import Config

# 🛡️ Configure retry logic for boto3 clients to handle transient errors like throttling
boto_retry_config = Config(
    retries={
        "max_attempts": 6,   # 🔁 Total number of attempts = 1 original + 5 retries
        "mode": "standard"   # 📊 'standard' = exponential backoff with jitter (default); 'adaptive' is dynamic based on load
    }
)

# 🔧 Create AWS service clients with retry config applied
s3 = boto3.client('s3', config=boto_retry_config)                     # Used for downloading and uploading ZIPs and reports
ddb = boto3.resource('dynamodb')                                      # Used to log metadata of grading
bedrock = boto3.client('bedrock-agent-runtime', config=boto_retry_config)  # Calls the Bedrock agent for grading

# 🌐 Environment variable configuration
SOURCE_BUCKET = os.environ['SOURCE_BUCKET']
REPORT_BUCKET = os.environ['REPORT_BUCKET']
TABLE_NAME = os.environ['DDB_TABLE']
AGENT_ID = os.environ['AGENT_ID']
AGENT_ALIAS_ID = os.environ['AGENT_ALIAS_ID']

# 🚀 Lambda entry point
def lambda_handler(event, context):
    for record in event['Records']:
        try:
            # 📩 Parse the message from SQS
            message = json.loads(record['body'])
            print("Message2:", message)

            # 📌 Extract metadata
            s3_key = message['s3_key']
            email = message.get('email', 'unknown')
            submission_id = message.get('submission_id', f"sub-{datetime.utcnow().isoformat()}")

            # 📥 Download the ZIP file from S3
            zip_obj = s3.get_object(Bucket=SOURCE_BUCKET, Key=s3_key)
            zip_data = zip_obj['Body'].read()

            # 🧵 Unzip and extract valid .py and .js source files
            with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
                valid_files = [f for f in z.namelist() if f.endswith(('.py', '.js'))]
                if not valid_files:
                    raise ValueError("No valid source files found")
                code = {f: z.read(f).decode('utf-8') for f in valid_files}

            # 📦 Prepare prompt for Bedrock agent
            prompt = {"input": {"source_code_files": code}}

            # 🧠 Call the Bedrock agent with retry-enabled client
            response = bedrock.invoke_agent(
                agentId=AGENT_ID,
                agentAliasId=AGENT_ALIAS_ID,
                sessionId=submission_id,
                inputText=json.dumps(prompt),
            )

            # 📡 Collect streaming response text
            response_text = ""
            for event in response["completion"]:
                chunk = event.get("chunk", {}).get("bytes", b"")
                response_text += chunk.decode("utf-8")

            print("Raw response text:\n", response_text)

            # 🧠 Try parsing response as structured JSON
            try:
                feedback = json.loads(response_text)
            except json.JSONDecodeError:
                feedback = {
                    "submission_id": submission_id,
                    "raw_feedback": response_text.strip()  # fallback to raw string if JSON fails
                }

            print("Parsed feedback:", feedback)

            # 💾 Save grading report to S3
            report_key = f"{submission_id}/grading_report.json"
            s3.put_object(Bucket=REPORT_BUCKET, Key=report_key, Body=json.dumps(feedback))

            # 🗃️ Log result metadata in DynamoDB
            ddb.Table(TABLE_NAME).put_item(Item={
                "submission_id": submission_id,
                "email": email,
                "timestamp": datetime.utcnow().isoformat(),
                "report_key": report_key,
                "feedback_summary": feedback.get("summary", "N/A")
            })

        except Exception as e:
            # ❌ Print and propagate errors so Lambda will retry if needed
            print(f"❌ Error: {str(e)}")
            raise

    return {"status": "done"}
