import requests
import streamlit as st

def get_signed_url(filename, email):
    response = requests.post(st.secrets["api"]["SIGNED_URL_ENDPOINT"], json={
        "filename": filename,
        "email": email
    })
    return response.json().get("signed_url")

def upload_cleaned_zip(signed_url, zip_data):
    headers = {"Content-Type": "application/zip"}
    return requests.put(signed_url, data=zip_data, headers=headers)
