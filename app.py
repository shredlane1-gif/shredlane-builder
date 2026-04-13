import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Shredlane Prime Master", layout="wide")
st.title("⚡ Shredlane Prime: Automation Hub")

# Load Secrets
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account") 

# --- DIAGNOSTIC CHECK ---
if api_key:
    st.sidebar.success("✅ API Key detected")
else:
    st.sidebar.error("❌ API Key NOT detected")

# Initialize Gemini Model (Updated for 2026 Models)
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Using Gemini 3 Flash - the current standard for 2026
        model = genai.GenerativeModel("gemini-3-flash")
        st.sidebar.info("Model: Gemini 3 Flash")
    except Exception as e:
        # Fallback to 2.5 if 3.0 is having high demand
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            st.sidebar.warning("Model: Gemini 2.5 Fallback")
        except:
            st.error(f"AI Configuration Error: {e}")

# Initialize Google Sheets Connection
def get_sheet():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(google_creds, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        st.error(f"Google Sheets Connection Error: {e}")
        return None

# --- 2. DATA PARSER ---
def extract_metrics(text):
    metrics = {
        "weight": re.search(r"Weight:\s*(\d+\.?\d*)", text, re.IGNORECASE),
        "waist": re.search(r"Waist:\s*(\d+\.?\d*)", text, re.IGNORECASE),
        "steps": re.search(r"Steps:\s*(\d+)", text, re.IGNORECASE),
        "sleep": re.search(r"Sleep:\s*(\d+)", text, re.IGNORECASE),
    }
    return {k: (v.group(1) if v else "Not reported") for k, v in metrics.items()}

# --- 3. ACCESS CONTROL ---
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])
password = st
