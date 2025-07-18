import streamlit as st
from utils.cleaner import clean_code_content
import zipfile
import io

st.title("📂 Upload and Clean Code Submission")

uploaded = st.file_uploader("Upload your ZIP file", type=["zip"])

if uploaded:
    zip_bytes = uploaded.read()

    # ✅ Size Check
    MAX_SIZE_MB = 5
    MAX_BYTES = MAX_SIZE_MB * 1024 * 1024
    if len(zip_bytes) > MAX_BYTES:
        st.error(f"❌ File too large. Please upload a ZIP smaller than {MAX_SIZE_MB} MB.")
        st.stop()

    # 📂 Show ZIP file list
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        file_list = z.namelist()

    with st.expander("📁 View files inside uploaded ZIP"):
        st.write(f"Total files: {len(file_list)}")
        st.code("\n".join(file_list))

    # 🧹 Clean the code with spinner
    with st.spinner("🧹 Cleaning and filtering files..."):
        try:
            cleaned_zip, file_cleaned, file_raw = clean_code_content(zip_bytes)
        except Exception as e:
            st.error(f"❌ Failed to clean ZIP: {e}")
            st.stop()

    # 📏 Display sizes and stats
    st.info(f"📦 Original ZIP size: {len(zip_bytes)/1024:.2f} KB")
    st.success(f"🧹 Cleaned ZIP size: {len(cleaned_zip)/1024:.2f} KB")
    st.write(f"🗂️ Files kept after cleaning: {file_cleaned} / {file_raw}")

    # ⬇️ Download button
    st.download_button(
        "⬇️ Download Cleaned ZIP",
        data=cleaned_zip,
        file_name="cleaned.zip",
        mime="application/zip"
    )
