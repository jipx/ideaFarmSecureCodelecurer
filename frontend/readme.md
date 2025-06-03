# 🛡️ Secure Coding Grader (Streamlit)

This app allows students to upload `.zip` files containing `.js` or `.py` code, clean them by removing comments and unnecessary content, and submit them for grading via AWS Bedrock (Claude 4). The backend uses S3 for storage and optionally logs submissions to DynamoDB.

---

## 🚀 Features

- ✅ Secure ZIP upload and in-browser preview
- ✅ Removal of:
  - Node modules and large libraries
  - Full-line and inline comments
  - Multiline comments (`/* ... */`, `''' ... '''`, `""" ... """`)
  - Blank lines
- ✅ Side-by-side original vs cleaned file preview
- ✅ Estimate token usage before submission
- ✅ Submit cleaned zip to S3 using signed URL
- ✅ Store submission metadata (email, tokens, filename)
- ✅ Optional toggle to enable/disable cleaning
- ✅ `max_tokens` slider to control Bedrock response length

---

## 🎛 Understanding `max_tokens`

Claude 4 models (like Opus or Sonnet) on AWS Bedrock apply this rule:

```
Quota used = input_tokens × 1 + output_tokens × 5
```

### Why `max_tokens` matters:

- **Controls Claude's output length** (e.g. feedback verbosity)
- **Limits quota usage** and prevents throttling
- **Impacts concurrency and grading speed**

### Example:

- Input code: 5,000 tokens
- `max_tokens = 100` → total quota = 5,000 + (100 × 5) = 5,500
- `max_tokens = 1000` → total quota = 10,000

### In the app:

You can choose:
- 🔹 Concise feedback → 200 tokens
- 🔸 Standard → 500 tokens
- 🔸 Verbose → 1000+ tokens

Set using:

```python
max_tokens = st.slider("Max output tokens", 100, 2000, value=300)
```

---

## 📦 Project Structure

```
secure-code-grader/
├── app.py
├── pages/
│   ├── 1_Upload_and_Clean.py
│   ├── 2_View_Submissions.py
├── utils/
│   ├── cleaner.py
│   ├── s3_upload.py
├── .streamlit/
│   └── secrets.toml
├── requirements.txt
├── README.md
```

---

## 🔐 Secrets Configuration (`.streamlit/secrets.toml`)

```toml
[api]
SIGNED_URL_ENDPOINT = "https://your-api.com/get-signed-url"
RECORD_SUBMISSION_ENDPOINT = "https://your-api.com/record-submission"
```

---

## 📎 Requirements

- Streamlit
- Requests
- AWS credentials for S3 signed URL (backend Lambda)
