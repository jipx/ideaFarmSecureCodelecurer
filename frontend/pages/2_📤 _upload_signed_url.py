import streamlit as st
import requests
import urllib.parse
import os
import time
from urllib.parse import urlparse

st.title("📄 Upload ZIP to S3 Using Signed URL")

# Inputs
student_id = st.text_input("Student ID", value="jipx901")
email = st.text_input("Email", value="student001@example.com")
zip_file = st.file_uploader("Upload ZIP file", type=["zip"])

MAX_SIZE_MB = 5

if st.button("Get Signed URL and Upload") and zip_file:
    if zip_file.size > MAX_SIZE_MB * 1024 * 1024:
        st.warning(f"🚫 File exceeds {MAX_SIZE_MB}MB limit")
        st.stop()

    with st.spinner("⏳ Uploading..."):
        # Dynamically resolve path to image
        CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
        GIF_PATH = os.path.join(CURRENT_DIR, "..", "images", "inprogress.gif")

        if os.path.exists(GIF_PATH):
            st.image(GIF_PATH, width=200)
        else:
            st.warning("⚠️ Progress image not found.")

        try:
            api_url = st.secrets["apigateway"]["signed_url_api"]
            status_api_url = st.secrets["apigateway"]["status_api_url"]

            payload = {
                "student_id": student_id,
                "email": email,
                "filename": zip_file.name
            }

            st.write("📡 Requesting signed URL...")
            st.json(payload)

            api_response = requests.post(api_url, json=payload, timeout=10)
            st.write("📥 Response from signed URL API:")
            st.json(api_response.json())
            api_response.raise_for_status()
            response_json = api_response.json()
            signed_url = response_json.get("url")
            if not signed_url:
                st.error("❌ Backend did not return a presigned URL under 'url'.")
                st.json(response_json)
                st.stop()

            object_key = response_json.get("s3_key", f"submissions/{student_id}/submission.zip")
            st.code(signed_url, language="text")

            upload_headers = {"Content-Type": "application/zip"}
            response = requests.put(signed_url, data=zip_file.getvalue(), headers=upload_headers)

            if response.status_code == 200:
                st.success("✅ File uploaded successfully to S3")
                parsed = urlparse(signed_url)
                s3_url = f"https://{parsed.netloc}/{urllib.parse.quote(object_key)}"
                st.markdown(f"**S3 Object URL:** [{s3_url}]({s3_url})")

                # Polling for grading status
                status_url = f"{status_api_url}?submission_id={student_id}"
                polling_message = st.empty()
                download_link = st.empty()

                for i in range(10):
                    time.sleep(3)
                    try:
                        status_response = requests.get(status_url, {}, timeout=5)
                    except requests.exceptions.Timeout:
                        polling_message.warning(f"⚠️ Unable to fetch status (attempt {i + 1})")
                        continue

                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        status = status_data.get("status", "unknown").lower()
                        if status == "completed":
                            report_url = status_data.get("report_url")
                            polling_message.success("✅ Grading completed!")
                            download_link.markdown(f"[Download Report]({report_url})", unsafe_allow_html=True)
                            break
                        elif status == "failed":
                            polling_message.error("❌ Grading failed.")
                            break
                        else:
                            polling_message.info(f"⏳ Grading Status: {status.capitalize()} (Attempt {i + 1})")
                    else:
                        polling_message.warning(f"⚠️ Unable to fetch status (attempt {i + 1})")

                if i == 9:
                    polling_message.warning("⏳ Grading still in progress. Please check back later.")

            else:
                st.error(f"❌ Upload failed: {response.status_code} - {response.text}")
                st.code(response.headers, language="json")

        except Exception as e:
            st.error(f"❌ Error uploading: {e}")
else:
    st.info("Fill in the student ID and email, upload a ZIP, and click the button.")
