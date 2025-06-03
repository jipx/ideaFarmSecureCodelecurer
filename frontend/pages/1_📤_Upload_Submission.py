
import streamlit as st
import uuid
import requests

st.set_page_config(page_title="📤 Upload Submission", layout="wide")
st.title("📤 Submit Your Source Code for Grading")

SIGNED_URL_API = st.secrets["SIGNED_URL_API"]  # e.g. https://api.example.com/get-signed-url
submission_id = str(uuid.uuid4())
uploaded_file = st.file_uploader("Upload ZIP file", type=["zip"])

if uploaded_file:
    if not uploaded_file.name.endswith(".zip"):
        st.error("Only .zip files are allowed.")
    else:
        with st.spinner("Requesting signed upload URL..."):
            res = requests.post(SIGNED_URL_API, json={"submission_id": submission_id})
            if res.status_code != 200:
                st.error(f"Failed to get signed URL: {res.text}")
                st.stop()

            upload_url = res.json().get("upload_url")
            if not upload_url:
                st.error("Upload URL not returned from backend.")
                st.stop()

        with st.spinner("Uploading ZIP to S3..."):
            headers = {"Content-Type": "application/zip"}
            upload_response = requests.put(upload_url, data=uploaded_file.getvalue(), headers=headers)

        if upload_response.status_code == 200:
            st.success("✅ Uploaded successfully.")
            st.info(f"🆔 Your submission ID: `{submission_id}`")
            st.session_state["submission_id"] = submission_id
        else:
            st.error(f"❌ Upload failed with status {upload_response.status_code}")
