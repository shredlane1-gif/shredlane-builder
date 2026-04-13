import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Shredlane Prime Master", layout="wide")
st.title("⚡ Shredlane Prime: Automation Hub")

# Load Secrets
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account")

# --- SMART MODEL PICKER (Fixes 404 & NoneType errors) ---
model = None
if api_key:
    genai.configure(api_key=api_key)
    # 2026 Model Priority List
    model_variants = ["gemini-3-flash", "gemini-2.5-flash", "gemini-1.5-flash", "gemini-pro"]
    
    for m_name in model_variants:
        try:
            test_model = genai.GenerativeModel(m_name)
            # Connectivity Test
            test_model.generate_content("hi", generation_config={"max_output_tokens": 1})
            model = test_model
            st.sidebar.success(f"✅ AI Online: {m_name}")
            break
        except Exception:
            continue

    if model is None:
        st.sidebar.error("❌ AI Offline: Check API Key/Quotas")
else:
    st.sidebar.error("❌ Secrets Error: GOOGLE_API_KEY not found")

# --- 2. ACCESS CONTROL ---
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])
user_pass = st.sidebar.text_input("Master Password", type="password")

if not user_pass:
    st.info("🗝️ Enter Master Password in the sidebar to unlock system.")
    st.stop()

if user_pass != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
    st.error("❌ Incorrect Password.")
    st.stop()

# --- 3. GOOGLE SHEETS HELPER ---
def get_sheet():
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(google_creds, scopes=scopes)
        client = gspread.authorize(creds)
        return client.open_by_key(sheet_id).sheet1
    except Exception as e:
        st.error(f"Sheets Error: {e}")
        return None

# --- 4. AUDIT ENGINE ---
if mode == "Audit Engine":
    st.header("📋 Client Audit Engine")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name")
        targets = st.text_input("Daily Targets (e.g., 1800kcal / 140g P)")
    with col2:
        date_today = st.date_input("Check-in Date", datetime.now())
    
    whatsapp_data = st.text_area("Paste WhatsApp Stats:", height=100)
    diary_log = st.text_area("Paste MyNetDiary Log:", height=150)
    
    if st.button("🚀 Run Shredlane Audit"):
        if model is None:
            st.error("AI Engine is not connected. Check sidebar status.")
        elif "chicken" in diary_log.lower() and not any(cut in diary_log.lower() for cut in ["breast", "thigh", "wing", "drumstick", "leg"]):
            st.error("⚠️ Shredlane Violation: Specify the chicken cut (Breast/Thigh) and weigh without bones.")
        elif not client_name or not whatsapp_data:
            st.error("Please provide Client Name and WhatsApp data.")
        else:
            with st.spinner("Analyzing data..."):
                try:
                    doctrine = """
                    SYSTEM INSTRUCTION: You are the Shredlane Data Auditor.
                    - Format: Bullet points (•) only. NO DASHES.
                    - Metrics: Fats in GRAMS only. 
                    - Precision: Reject non-specific chicken. Require cut identification.
                    - Protein: Breast=23g/100g, Soy=50g/100g, Beef/Goat=20g/100g.
                    """
                    prompt = f"{doctrine}\n\nAUDIT: {client_name} | {targets} | {whatsapp_data} | {diary_log}"
                    
                    response = model.generate_content(prompt)
                    st.subheader(f"Results: {client_name}")
                    clean_text = response.text.replace("- ", "• ").replace("—", "")
                    st.markdown(clean_text)
                    st.code(clean_text, language="markdown")
                    
                    # Sync to Sheets
                    sheet = get_sheet()
                    if sheet:
                        w_match = re.search(r"Weight:\s*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                        weight = w_match.group(1) if w_match else "N/A"
                        sheet.append_row([str(date_today), client_name, weight])
                        st.toast(f"✅ Logged {client_name}'s weight to Sheets")
                except Exception as e:
                    st.error(f"Audit Crash: {e}")

# --- 5. MEAL BUILDER ---
elif mode == "Meal Builder":
    st.header("🛠 Shredlane Meal Builder")
    u_weight = st.text_input("Client Weight (kg)")
    u_ingredients = st.text_area("Available Ingredients")
    
    if st.button("Build Plan"):
        if model is None:
            st.error("AI Engine offline.")
        elif not u_weight or not u_ingredients:
            st.error("Provide weight and ingredients.")
        else:
            with st.spinner("Building Options..."):
                try:
                    res = model.generate_content(f"Shredlane Plan: {u_weight}kg, ingredients: {u_ingredients}. Two options. No dashes. Fats in grams.")
                    st.markdown(res.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Builder Error: {e}")
