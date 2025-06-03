# 🧠 How to Create a Bedrock Agent for Code Grading

## ✅ 1. Go to Amazon Bedrock Console
- URL: [https://console.aws.amazon.com/bedrock](https://console.aws.amazon.com/bedrock)
- Use a supported region like `us-east-1`

## ✅ 2. Create a New Agent
- Click **“Agents”** in the sidebar
- Click **“Create Agent”**
- Set:
  - **Name:** `SecureCodeGrader`
  - **Description:** `Grades secure coding submissions using Bedrock`
  - **Foundation Model:** Claude 3 Sonnet (or similar)

## ✅ 3. Define Prompt Template
```
You are a secure coding grading assistant. Review the provided source code and grade it based on these 5 categories:
1. Input validation
2. Authentication and session management
3. Authorization and access control
4. Error handling and logging
5. Data protection and encryption

Respond in JSON with:
{
  "score": 0-100,
  "strengths": [ ... ],
  "improvements": [ ... ]
}

Code:
{{code_input}}
```
- Define a variable: `code_input`

## ✅ 4. (Optional) Add Action Group
- Add if you want it to trigger Lambda (can be skipped)

## ✅ 5. Deploy the Agent
- Click **Deploy**
- Note `AgentId` and `AgentAliasId`

## ✅ 6. Test the Agent
Sample payload:
```json
{
  "code_input": "def login(user, pwd):\n  if user in db: return True\n  return False"
}
```

## ✅ 7. Call from Lambda
```python
import boto3

client = boto3.client('bedrock-agent-runtime')
response = client.invoke_agent(
    agentId='AGENT_ID',
    agentAliasId='AGENT_ALIAS_ID',
    sessionId='unique-session-id',
    inputText='code_input: your_code_here'
)
```

## 🧠 Model Comparison for Secure Coding Grading

When evaluating models for grading secure code submissions, it's important to compare them based on their ability to analyze code, identify security vulnerabilities, and produce structured feedback. Below is a comparison of three prominent Bedrock-supported models for this use case:

| Model              | Strengths                                                                 | Limitations                                                             | Suitability       |
|-------------------|---------------------------------------------------------------------------|-------------------------------------------------------------------------|-------------------|
| **Claude 3.5 Sonnet** | - Strong contextual understanding<br>- Good with secure coding feedback<br>- Balanced performance and speed | - May require fine-tuning for domain-specific grading rubrics         | ⭐ Recommended     |
| **Titan Text Express** | - Fast inference times<br>- Handles general tasks well                   | - Limited depth in complex code logic and secure practices             | 🔸 Good fallback  |
| **Mistral**           | - Creative suggestions<br>- Lightweight model                           | - Less reliable on structured grading<br>- Not security-specialized    | ⚠️ Not ideal      |

**Recommendation:** Claude 3.5 Sonnet is the best candidate for secure coding grading tasks due to its deep reasoning capabilities and ability to provide feedback aligned with OWASP principles.


## 🔍 Secure Coding Model Comparison (AWS Bedrock)

The grading system integrates AWS Bedrock Agents and various foundation models. Below is a comparison of models tested for secure coding grading tasks:

| Model              | Max Tokens | Cost (USD / 1M tokens)**         | Latency   | Reasoning Quality | Strengths                                     | Weaknesses                                      |
|-------------------|------------|----------------------------------|-----------|--------------------|-----------------------------------------------|------------------------------------------------|
| **Claude 3 Opus** | 200,000    | ~$15.00 (input), ~$75.00 (output)| Medium    | ⭐⭐⭐⭐⭐             | Best for large ZIP grading, deep OWASP reasoning | High output cost, throttled under free tier    |
| **Claude 3 Sonnet** | 200,000  | ~$3.00 (input), ~$15.00 (output) | Fast      | ⭐⭐⭐⭐              | Ideal balance of performance and cost         | Slightly less accurate on nuanced logic        |
| **Claude 3 Haiku** | 200,000   | ~$0.25 (input), ~$1.25 (output)  | Very Fast | ⭐⭐⭐               | Great for fast feedback, small code checks    | Limited understanding of complex secure code   |
| **Command R+**    | 128,000    | ~$0.60 / 1M tokens total          | Medium    | ⭐⭐⭐⭐              | Strong for structured grading + retrieval     | May need prompt tuning for coding nuance       |
| **Titan Text G1** | 8,192      | ~$0.75 / 1M tokens total          | Fast      | ⭐⭐                | Fast AWS-native option                        | Token limit too low for multi-file grading     |
| **Llama 3 70B**   | 8,192      | ~$1.50 / 1M tokens                | Medium    | ⭐⭐⭐⭐              | Natural explanations, good at OWASP terms     | Not optimized for secure coding logic          |
| **Mistral 7B**    | 32,000     | ~$0.45 / 1M tokens                | Very Fast | ⭐⭐                | Light and fast                                | Lacks accuracy for structured secure review    |

**Prices approximate as of 2025 and subject to change.

### 🏆 Recommendations

| Use Case                           | Recommended Model      | Why?                                       |
|------------------------------------|------------------------|--------------------------------------------|
| Full ZIP file with OWASP scoring   | **Claude 3 Opus**      | Handles large context, precise reasoning   |
| Cost-effective, fast review        | **Claude 3 Sonnet**    | Balanced price and output                  |
| Instant feedback (small code)      | **Claude 3 Haiku**     | Fastest, low-cost model                    |
| Feedback with document retrieval   | **Command R+**         | Strong RAG support                         |
