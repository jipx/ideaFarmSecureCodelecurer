
import streamlit as st
import urllib.parse
import time

# === Cognito Configuration ===
COGNITO_DOMAIN = st.secrets["cognito"]["COGNITO_DOMAIN"]
CLIENT_ID = st.secrets["cognito"]["CLIENT_ID"]
REDIRECT_URI = st.secrets["cognito"]["REDIRECT_URI"]

def get_login_url():
    return (
        f"{COGNITO_DOMAIN}/oauth2/authorize?response_type=code"
        f"&client_id={CLIENT_ID}&redirect_uri={urllib.parse.quote(REDIRECT_URI)}"
        f"&scope=openid+profile+email"
    )

def get_logout_url():
    return (
        f"{COGNITO_DOMAIN}/logout?"
        f"client_id={CLIENT_ID}&"
        f"logout_uri={urllib.parse.quote(REDIRECT_URI)}"
    )

st.set_page_config(page_title="🏠 Secure Coding Grader", layout="wide")
st.title("🏠 Secure Coding Grader Home")

# === Auth Buttons ===
st.markdown("## 🔐 Authentication")

col1, col2 = st.columns([1, 1])
with col1:
    st.link_button("🔓 Login with Cognito", get_login_url())
with col2:
    st.link_button("🚪 Logout", get_logout_url())

# === Description ===
st.markdown("""
---

### 🧑‍🎓 For Students:
- 📤 **Upload Submission**: Submit your `.zip` file for grading.
- 🔔 **Wait for Grading**: Automatically refresh to check your score.
- 📄 **Get Result**: Retrieve report using submission ID.

### 👩‍🏫 For Lecturers:
- 📊 **Instructor Dashboard**
- 📊 **Grading Log**
- ⚙️ **Admin Rule Editor**

### ⚙️ Backend:
- AWS Bedrock Agent
- S3 + SQS + Lambda + DDB
""")
