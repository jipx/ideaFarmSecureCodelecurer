import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AWS EventBridge Workflow", layout="wide")

st.title("📦 AWS EventBridge File Submission Flow")
st.markdown("""
This Streamlit app visualizes the AWS EventBridge integration workflow:
1. A `.zip` file is uploaded to S3  
2. EventBridge filters and transforms the event  
3. Message is pushed to SQS  
4. Lambda processes the submission for grading  
""")

# Load and display the HTML animation
with open("Eventbridge.html", 'r', encoding='utf-8') as f:
    html_content = f.read()

components.html(html_content, height=2000, scrolling=True)
