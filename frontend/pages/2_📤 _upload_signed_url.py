
import streamlit as st
import requests
import urllib.parse
import os
import time

st.title("📤 Upload ZIP to S3 Using Signed URL")

# Inputs
student_id = st.text_input("Student ID", value="jipx901")
email = st.text_input("Email", value="student001@example.com")
zip_file = st.file_uploader("Upload ZIP file", type=["zip"])

if st.button("Get Signed URL and Upload") and zip_file:
    with st.spinner("⏳ Uploading..."):
        st.image("images/inprogress.gif", width=200)

        try:
            api_url = st.secrets["signed_url_api"]
            status_api_url = st.secrets["status_api"]
            payload = {"student_id": student_id, "email": email}
            headers = {"x-api-key": st.secrets["api_key"]}
            api_response = requests.post(api_url, json=payload, headers=headers)
            api_response.raise_for_status()
            signed_url = api_response.json()["signed_url"]
            object_key = api_response.json().get("s3_key", f"submissions/{student_id}/submission.zip")

            st.code(signed_url, language="text")

            upload_headers = {
                "Content-Type": "application/zip",
                "x-amz-meta-submission_id": student_id,
                "x-amz-meta-email": email
            }

            response = requests.put(signed_url, data=zip_file.getvalue(), headers=upload_headers)
            if response.status_code == 200:
                st.success("✅ File uploaded successfully to S3")
                s3_url = f"https://{signed_url.split('/')[2]}/{urllib.parse.quote(object_key)}"
                st.markdown(f"**S3 Object URL:** [{s3_url}]({s3_url})")

                # --- Polling for grading status ---
                status_url = f"{status_api_url}?submission_id={student_id}"
                polling_message = st.empty()
                download_link = st.empty()

                for i in range(10):
                    time.sleep(3)
                    status_response = requests.get(status_url, headers={"x-api-key": st.secrets["api_key"]})
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
        except Exception as e:
            st.error(f"❌ Error uploading: {e}")
else:
    st.info("Fill in the student ID and email, upload a ZIP, and click the button.")
