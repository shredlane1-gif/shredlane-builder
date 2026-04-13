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
    st.sidebar.success("✅ API Key detected in Secrets")
else:
    st.sidebar.error("❌ API Key NOT detected")

# Initialize Gemini Model
if api_key:
    try:
        genai.configure(api_key=api_key)
        # UPDATED: Using the standard full model path to fix the 404
        model = genai.GenerativeModel("models/gemini-1.5-flash")
    except Exception as e:
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
password = st.sidebar.text_input("Master Password", type="password")

if not password:
    st.info("🗝️ Enter the Master Password in the sidebar to unlock.")
    st.stop()

if password != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
    st.error("❌ Incorrect Password.")
    st.stop()

# --- 4. AUDIT ENGINE ---
if mode == "Audit Engine":
    st.subheader("📋 Shredlane Data Auditor")
    with st.form("audit_form"):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Client Name")
            targets = st.text_input("Daily Targets")
        with col2:
            date_today = st.date_input("Check-in Date", datetime.now())
        
        whatsapp_data = st.text_area("Paste WhatsApp Check-in:")
        diary_log = st.text_area("Paste MyNetDiary Log:")
        submit_audit = st.form_submit_button("Generate Audit & Sync")

    if submit_audit:
        if not client_name or not whatsapp_data:
            st.warning("⚠️ Missing data. Please paste the WhatsApp check-in.")
        else:
            metrics = extract_metrics(whatsapp_data)
            
            doctrine_prompt = f"""
            You are the Shredlane Data Auditor. Adhere to SHREDLANE DOCTRINE:
            1. PROTEIN: Soy Chunks (100g)=50g, Chicken Breast (100g)=23g, Beef (100g)=20g, Eggs (1)=6g.
            2. NO DASHES: Never use '-' or '—'. Use bullet points or numbers.
            3. FATS: Must be in GRAMS.
            
            INPUT: {client_name} | {targets} | {whatsapp_data} | {diary_log}
            """
            
            with st.spinner("Analyzing and Syncing..."):
                try:
                    response = model.generate_content(doctrine_prompt)
                    if response and response.text:
                        st.success("Audit Complete")
                        clean_feedback = response.text.replace("- ", "• ").replace("—", "")
                        st.markdown(clean_feedback)
                        st.code(clean_feedback, language="markdown")
                        
                        sheet = get_sheet()
                        if sheet:
                            new_row = [str(date_today), client_name, metrics["weight"], metrics["waist"], metrics["steps"], metrics["sleep"]]
                            sheet.append_row(new_row)
                            st.toast("✅ Logged to Sheets!")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- 5. MEAL BUILDER ---
elif mode == "Meal Builder":
    st.subheader("🛠 Shredlane Meal Builder")
    with st.form("meal_form"):
        weight = st.text_input("Weight (kg)")
        ingredients = st.text_area("Ingredients")
        if st.form_submit_button("Build Plan"):
            if not weight or not ingredients:
                st.error("Fill in weight and ingredients.")
            else:
                with st.spinner("Building..."):
                    res = model.generate_content(f"Shredlane Meal Plan (No dashes, fats in grams): {weight}kg, {ingredients}")
                    st.markdown(res.text.replace("- ", "• "))
