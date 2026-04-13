import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Shredlane Prime", layout="wide")
st.title("⚡ Shredlane Prime: Automation Hub")

# Load Secrets
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account")

# Sidebar Status & Setup
st.sidebar.header("System Status")
if api_key:
    st.sidebar.success("✅ API Key Loaded")
    try:
        genai.configure(api_key=api_key)
        # Using the standard 2026 model string
        model = genai.GenerativeModel("gemini-3-flash")
    except Exception as e:
        st.sidebar.error(f"AI Setup Error: {e}")
else:
    st.sidebar.error("❌ API Key Missing")

# --- 2. ACCESS CONTROL ---
# This is the "Gatekeeper"
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])
user_pass = st.sidebar.text_input("Enter Master Password", type="password")

if not user_pass:
    st.warning("🗝️ App Locked. Please enter the Master Password in the sidebar to reveal input fields.")
    st.stop()

if user_pass != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
    st.error("❌ Access Denied: Incorrect Password.")
    st.stop()

# --- 3. GOOGLE SHEETS HELPER ---
def get_sheet():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(google_creds, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        st.error(f"Sheets Connection Error: {e}")
        return None

# --- 4. AUDIT ENGINE ---
if mode == "Audit Engine":
    st.header("📋 Client Audit Engine")
    st.write("Fill in the details below to generate a Shredlane Doctrine audit.")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name")
        targets = st.text_input("Daily Targets")
    with col2:
        date_today = st.date_input("Check-in Date", datetime.now())
    
    whatsapp_data = st.text_area("Paste WhatsApp Stats (Weight, Waist, etc.):", height=100)
    diary_log = st.text_area("Paste MyNetDiary Food Log:", height=150)
    
    if st.button("Generate & Sync"):
        if not client_name or not whatsapp_data:
            st.error("Missing required fields!")
        else:
            with st.spinner("Analyzing..."):
                try:
                    # Logic for the Audit
                    prompt = f"Audit this based on Shredlane Doctrine (No dashes, fats in grams): {whatsapp_data} {diary_log}"
                    response = model.generate_content(prompt)
                    st.subheader(f"Audit Results for {client_name}")
                    st.markdown(response.text.replace("- ", "• "))
                    
                    # Try to sync to sheets
                    sheet = get_sheet()
                    if sheet:
                        # Simple regex to find the weight
                        w_match = re.search(r"Weight:\s*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                        weight = w_match.group(1) if w_match else "N/A"
                        sheet.append_row([str(date_today), client_name, weight])
                        st.toast("✅ Sheet Updated!")
                except Exception as e:
                    st.error(f"Audit Error: {e}")

# --- 5. MEAL BUILDER ---
elif mode == "Meal Builder":
    st.header("🛠 Shredlane Meal Builder")
    u_weight = st.text_input("Client Weight (kg)")
    u_ingredients = st.text_area("Available Ingredients")
    
    if st.button("Build Shredlane Plan"):
        with st.spinner("Calculating..."):
            try:
                res = model.generate_content(f"Shredlane Meal Plan: {u_weight}kg using {u_ingredients}")
                st.markdown(res.text.replace("- ", "• "))
            except Exception as e:
                st.error(f"Meal Builder Error: {e}")
