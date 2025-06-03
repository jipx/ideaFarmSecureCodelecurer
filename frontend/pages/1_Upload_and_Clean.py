import streamlit as st
from utils.cleaner import clean_code_content
from utils.s3_upload import upload_cleaned_zip, get_signed_url
import zipfile
import io

st.title("📂 Upload and Clean Code Submission")
uploaded = st.file_uploader("Upload your ZIP file", type=["zip"])
if uploaded:
    zip_bytes = uploaded.read()
    cleaned_zip, file_cleaned, file_raw = clean_code_content(zip_bytes)
    st.download_button("⬇️ Download Cleaned ZIP", data=cleaned_zip, file_name="cleaned.zip", mime="application/zip")
