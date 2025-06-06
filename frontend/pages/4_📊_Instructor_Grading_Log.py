import streamlit as st
import requests
import pandas as pd

# Configure Streamlit page
st.set_page_config(page_title="📊 Grading Dashboard", layout="wide")
st.title("📊 Instructor Grading Dashboard")

# API endpoint (replace with actual secret or static value)
API_ENDPOINT = st.secrets.get("DASHBOARD_API", "https://your-api-url/dashboard")

# Button to trigger refresh
st.info("Click below to fetch grading results.")
if st.button("🔄 Refresh Dashboard"):
    try:
        response = requests.get(API_ENDPOINT)
        response.raise_for_status()
        data = response.json()
        df = pd.DataFrame(data.get("results", []))

        if df.empty:
            st.warning("No grading results found.")
        else:
            st.success("✅ Results loaded.")

            # --- Filters ---
            with st.expander("🔍 Filter Options"):
                name_filter = st.text_input("Search by student name or ID")
                min_score = st.slider("Minimum Score", 0, 100, 0)
                max_score = st.slider("Maximum Score", 0, 100, 100)

            # Apply filters
            if name_filter:
                df = df[df.apply(lambda row: name_filter.lower() in str(row).lower(), axis=1)]
            df = df[(df["score"] >= min_score) & (df["score"] <= max_score)]

            # --- Add icons and links ---
            def render_status_icon(status):
                return "✅" if status == "complete" else "⏳"

            def make_link(url):
                if pd.notna(url) and url.startswith("http"):
                    return f"[📄 View Report]({url})"
                return "—"

            df["status_icon"] = df["status"].apply(render_status_icon)
            df["report_link"] = df["report_url"].apply(make_link)

            # Reorder columns for display
            display_df = df[["submission_id", "status_icon", "score", "report_link"]]

            # Render table with markdown for report links
            st.markdown("### 🧾 Grading Results")
            st.dataframe(display_df)

            # Allow download
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download Filtered CSV", csv, "filtered_results.csv", "text/csv")

    except Exception as e:
        st.error(f"Failed to fetch data: {e}")