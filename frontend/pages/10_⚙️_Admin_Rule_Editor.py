import streamlit as st
import json
import sys
import os

# Add utils directory to sys.path for import
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "utils")))
from load_rules import load_rules, save_rules

# Configure page title and layout
st.set_page_config(page_title="🛠️ Edit Grading Rules", layout="wide")

st.title("🛠️ Admin Panel - Edit Grading Rules")

# Load existing grading rules
rules = load_rules()

# --- Allowed File Extensions ---
st.subheader("Allowed File Extensions")
extensions = st.text_input("Enter comma-separated file extensions", ", ".join(rules.get("allowed_extensions", [])))
rules["allowed_extensions"] = [ext.strip() for ext in extensions.split(",") if ext.strip()]

# --- Directories to Exclude ---
st.subheader("Exclude Directories")
excluded = st.text_input("Enter comma-separated directories to exclude", ", ".join(rules.get("exclude_dirs", [])))
rules["exclude_dirs"] = [d.strip() for d in excluded.split(",") if d.strip()]

# --- Secure Code Pattern Requirements ---
st.subheader("Required Secure Code Patterns")
patterns = st.text_area("One per line", "\n".join(rules.get("required_security_patterns", [])))
rules["required_security_patterns"] = [p.strip() for p in patterns.split("\n") if p.strip()]

# --- Minimum Passing Score ---
st.subheader("Minimum Score Threshold")
rules["min_score_threshold"] = st.slider("Score Threshold", 0, 100, rules.get("min_score_threshold", 60))

# --- Save Changes ---
if st.button("💾 Save Rules"):
    save_rules(rules)
    st.success("Rules saved successfully.")

# --- Display JSON for Review ---
st.subheader("📄 Current Rules JSON")
st.code(json.dumps(rules, indent=2), language="json")