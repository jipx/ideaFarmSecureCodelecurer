
# 🔐 Secure WAF Stack (AWS CDK)

This AWS CDK project deploys a Web Application Firewall (WAFv2) with:

- ✅ IP allowlist rule (Admin IP)
- ✅ Rate-based throttling
- ✅ Region header blocking (`X-Client-Region`)
- 🚨 Emergency "Block All" switch via SSM Parameter Store
- 🔁 Lambda function to toggle blocking dynamically
- 🔗 WebACL associations with **multiple Regional API Gateway** stages

---

## 📁 Project Structure

```
secure-waf-cdk/
├── app.py
├── cdk.json
├── README.md
├── secure_waf_stack.py
├── requirements.txt
```

---

## ⚙️ Prerequisites

- AWS CDK v2
- Python 3.11+
- AWS CLI (`aws configure`)
- CDK bootstrap:  
  ```bash
  cdk bootstrap
  ```

---

## 🚀 Deploy

### ✅ Step 1: Provide API Gateway ARNs

Only **Regional REST APIs** are supported by AWS WAF.

Edit `cdk.json`:

```json
{
  "app": "python app.py",
  "context": {
    "apis": [
      { "arn": "arn:aws:apigateway:us-east-1::/restapis/abcd1234/stages/prod" },
      { "arn": "arn:aws:apigateway:us-east-1::/restapis/efgh5678/stages/v1" }
    ]
  }
}
```

> You may also pass via CLI:  
> `cdk deploy --context apis='[{"arn":"..."}]'`

---

### ✅ Step 2: Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

### ✅ Step 3: Deploy

```bash
cdk deploy
```

---

## 🚨 Emergency `BlockAll` Rule

A special WAF rule named `BlockAll` can block all traffic **except** requests that include a method named `__BLOCKALL__` (which no normal client would use). You can toggle between blocking and counting modes dynamically.

### ✅ Enabled (Block All Requests)

```json
{
  "Name": "BlockAll",
  "Priority": 1,
  "Statement": {
    "NotStatement": {
      "Statement": {
        "ByteMatchStatement": {
          "SearchString": "__BLOCKALL__",
          "FieldToMatch": {
            "Method": {}
          },
          "TextTransformations": [
            {
              "Priority": 0,
              "Type": "NONE"
            }
          ],
          "PositionalConstraint": "EXACTLY"
        }
      }
    }
  },
  "Action": {
    "Block": {}
  },
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "BlockAll"
  }
}
```

### 🧪 Disabled (Count Only, for Testing)

```json
{
  "Name": "BlockAll",
  "Priority": 1,
  "Statement": {
    "NotStatement": {
      "Statement": {
        "ByteMatchStatement": {
          "SearchString": "__BLOCKALL__",
          "FieldToMatch": {
            "Method": {}
          },
          "TextTransformations": [
            {
              "Priority": 0,
              "Type": "NONE"
            }
          ],
          "PositionalConstraint": "EXACTLY"
        }
      }
    }
  },
  "Action": {
    "Count": {}
  },
  "VisibilityConfig": {
    "SampledRequestsEnabled": true,
    "CloudWatchMetricsEnabled": true,
    "MetricName": "BlockAll"
  }
}
```

---

## 📝 License

MIT (customize as needed)
