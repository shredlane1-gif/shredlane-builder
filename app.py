import streamlit as st
from google import genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Shredlane Prime", layout="wide", page_icon="⚡")
st.title("⚡ Shredlane Prime: Automation Hub")

# Accessing Secrets
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account")

# Initialize Client & Stable Model Detection
client = None
active_model = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        
        # We prioritize 1.5-Flash because 2.0-Flash is currently causing 'Expired' errors on free keys
        priority_names = [
            "models/gemini-1.5-flash", 
            "models/gemini-1.5-pro",
            "models/gemini-2.0-flash"
        ]
        
        available_models = [m.name for m in client.models.list()]
        for name in priority_names:
            if name in available_models:
                active_model = name
                break
        
        if active_model:
            st.sidebar.success(f"✅ System Online: {active_model}")
        else:
            st.sidebar.error("❌ No stable models found.")
    except Exception as e:
        st.sidebar.error(f"⚠️ Connection Failed: {e}")

# --- 2. SECURITY ---
st.sidebar.header("Navigation")
mode = st.sidebar.radio("Go to:", ["Audit Engine", "Meal Builder"])
user_pass = st.sidebar.text_input("Master Password", type="password")

if not user_pass:
    st.info("🗝️ Enter password to unlock.")
    st.stop()

if user_pass != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
    st.error("❌ Incorrect Password.")
    st.stop()

# --- 3. GOOGLE SHEETS SYNC ---
def sync_to_sheets(date, name, weight, waist, steps):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(google_creds, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(sheet_id).sheet1
        
        # Add a new row to ensure no data is overwritten
        sheet.append_row([str(date), name, weight, waist, steps], value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        st.error(f"Sheet Sync Error: {e}")
        return False

# --- 4. AUDIT ENGINE ---
if mode == "Audit Engine":
    st.header("📋 Client Audit Engine")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name")
        targets = st.text_input("Daily Targets (e.g. 1800kcal)")
    with col2:
        date_today = st.date_input("Check-in Date", datetime.now())
        client_gender = st.selectbox("Gender", ["Female", "Male"])
    
    whatsapp_data = st.text_area("Paste WhatsApp Stats:", height=100)
    diary_log = st.text_area("Paste MyNetDiary Log:", height=150)
    
    if st.button("🚀 Run Audit & Sync"):
        if "chicken" in diary_log.lower() and not any(cut in diary_log.lower() for cut in ["breast", "thigh", "wing", "drumstick", "leg"]):
            st.error("⚠️ SHREDLANE DOCTRINE: Specify chicken piece (e.g. Breast) and weigh bone-free.")
        elif not client_name or not whatsapp_data:
            st.error("Missing Client Name or Stats.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    doctrine_prompt = f"""
                    ROLE: Shredlane Auditor. 
                    TONE: Professional, firm, Grade 7 English.
                    RULES: 
                    - Bullet points (•) only. NO DASHES.
                    - Protein: Soy Chunks (100g)=50g, Chicken Breast (100g)=23g, Beef (100g)=20g, Fish (100g)=20g.
                    - If Female: Consider hormonal water retention.
                    
                    AUDIT: {client_name} ({client_gender}) | {targets} | {whatsapp_data} | {diary_log}
                    """
                    response = client.models.generate_content(model=active_model, contents=doctrine_prompt)
                    
                    st.subheader(f"Results for {client_name}")
                    st.markdown(response.text.replace("- ", "• "))
                    
                    # Extraction Logic
                    w = re.search(r"(?:wt|weight)[:\s]*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                    wa = re.search(r"(?:waist|wst)[:\s]*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                    s = re.search(r"(?:steps|st)[:\s]*(\d+)", whatsapp_data, re.IGNORECASE)
                    
                    if sync_to_sheets(date_today, client_name, w.group(1) if w else "N/A", wa.group(1) if wa else "N/A", s.group(1) if s else "N/A"):
                        st.toast("✅ Logged to Google Sheets!")
                except Exception as e:
                    st.error(f"Audit Crash: {e}")

# --- 5. MEAL BUILDER ---
elif mode == "Meal Builder":
    st.header("🛠 Shredlane Meal Builder")
    u_w = st.text_input("Weight (kg)")
    u_g = st.selectbox("Client Gender", ["Female", "Male"])
    u_i = st.text_area("Ingredients")
    
    if st.button("🏗️ Build Plan"):
        with st.spinner("Generating..."):
            try:
                res = client.models.generate_content(
                    model=active_model, 
                    contents=f"Build a Shredlane Plan for a {u_w}kg {u_g} using {u_i}. Two options. • bullets. Grade 7 English."
                )
                st.markdown(res.text.replace("- ", "• "))
            except Exception as e:
                st.error(f"Builder Error: {e}")
