import streamlit as st
from google import genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="Shredlane Prime", layout="wide")
st.title("⚡ Shredlane Prime: Automation Hub")

api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account")

# Initialize Client
client = None
# CHANGED: Using 'gemini-1.5-flash' as it is the most stable 2026 endpoint for v1beta
active_model = "gemini-1.5-flash" 

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        st.sidebar.success(f"✅ AI Online: {active_model}")
    except Exception as e:
        st.sidebar.error(f"Connection Failed: {e}")

# --- 2. SECURITY ---
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])
user_pass = st.sidebar.text_input("Master Password", type="password")

if not user_pass:
    st.info("🗝️ Enter password to unlock.")
    st.stop()

if user_pass != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
    st.error("❌ Incorrect Password.")
    st.stop()

# --- 3. GOOGLE SHEETS HELPER ---
def sync_to_sheets(date, name, weight, waist, steps):
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(google_creds, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet = gc.open_by_key(sheet_id).sheet1
        sheet.append_row([str(date), name, weight, waist, steps])
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
        targets = st.text_input("Daily Targets")
    with col2:
        date_today = st.date_input("Check-in Date", datetime.now())
    
    whatsapp_data = st.text_area("Paste WhatsApp Stats:", height=100)
    diary_log = st.text_area("Paste MyNetDiary Log:", height=150)
    
    if st.button("🚀 Run Audit & Sync"):
        # REJECTION LOGIC
        if "chicken" in diary_log.lower() and not any(cut in diary_log.lower() for cut in ["breast", "thigh", "wing", "drumstick", "leg"]):
            st.error("⚠️ SHREDLANE DOCTRINE: Specify chicken piece (e.g. Breast) and weigh bone-free.")
        elif not client_name or not whatsapp_data:
            st.error("Missing Client Name or Stats.")
        else:
            with st.spinner("Auditing..."):
                try:
                    doctrine_prompt = f"""
                    ROLE: Shredlane Auditor. 
                    TONE: Professional, firm, Grade 7 English. No jargon.
                    RULES: 
                    - Bullet points (•) only. NO DASHES.
                    - Fats: Must be in GRAMS. 
                    - Protein: Soy Chunks (100g)=50g, Chicken Breast (100g)=23g, Beef (100g)=20g, Eggs (1)=6g, Fish (100g)=20g.
                    - Feedback must be punchy. If data is missing, tell them to provide it in grams next time.
                    
                    AUDIT THIS: {client_name} | {targets} | {whatsapp_data} | {diary_log}
                    """
                    # New API models sometimes require 'models/' prefix depending on region
                    response = client.models.generate_content(
                        model=active_model, 
                        contents=doctrine_prompt
                    )
                    
                    st.subheader(f"Results for {client_name}")
                    clean_output = response.text.replace("- ", "• ").replace("—", "")
                    st.markdown(clean_output)
                    
                    # DATA EXTRACTION
                    weight = re.search(r"Weight:\s*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                    waist = re.search(r"Waist:\s*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                    steps = re.search(r"Steps:\s*(\d+)", whatsapp_data, re.IGNORECASE)
                    
                    w_val = weight.group(1) if weight else "N/A"
                    wa_val = waist.group(1) if waist else "N/A"
                    s_val = steps.group(1) if steps else "N/A"
                    
                    if sync_to_sheets(date_today, client_name, w_val, wa_val, s_val):
                        st.toast("✅ Logged to Google Sheets!")
                        
                except Exception as e:
                    st.error(f"Audit Crash: {e}")

# --- 5. MEAL BUILDER ---
elif mode == "Meal Builder":
    st.header("🛠 Shredlane Meal Builder")
    u_weight = st.text_input("Weight (kg)")
    u_ingredients = st.text_area("Ingredients")
    
    if st.button("Build Plan"):
        with st.spinner("Generating..."):
            try:
                res = client.models.generate_content(
                    model=active_model, 
                    contents=f"Shredlane Plan: {u_weight}kg, {u_ingredients}. Two options. No dashes. Fats in grams."
                )
                st.markdown(res.text.replace("- ", "• "))
            except Exception as e:
                st.error(f"Builder Error: {e}")
