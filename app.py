import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Shredlane Prime", layout="wide")
st.title("⚡ Shredlane Prime: Automation Hub")

api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account")

# --- SMART MODEL PICKER (Prevents 404) ---
model = None
if api_key:
    genai.configure(api_key=api_key)
    # List of models to try in order of preference
    for m_name in ["gemini-1.5-flash", "gemini-2.0-flash-exp", "gemini-pro"]:
        try:
            test_model = genai.GenerativeModel(m_name)
            # Minimal test call to verify availability
            test_model.generate_content("ping", generation_config={"max_output_tokens": 1})
            model = test_model
            st.sidebar.success(f"✅ System Online: {m_name}")
            break
        except:
            continue
else:
    st.sidebar.error("❌ API Key Missing")

# --- 2. ACCESS CONTROL ---
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])
user_pass = st.sidebar.text_input("Master Password", type="password")

if not user_pass:
    st.info("🗝️ Enter Master Password to unlock Shredlane Hub.")
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
        st.error(f"Sheets Connection Error: {e}")
        return None

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
    
    if st.button("Generate Audit & Sync"):
        # REJECTION LOGIC: Check for generic "chicken"
        if "chicken" in diary_log.lower() and not any(cut in diary_log.lower() for cut in ["breast", "thigh", "wing", "drumstick", "leg"]):
            st.error("⚠️ Error: Generic 'chicken' detected. Please specify the cut (e.g., Breast, Thigh) and weigh without bones.")
        elif not client_name or not whatsapp_data:
            st.error("Client Name and WhatsApp data are required.")
        else:
            with st.spinner("Processing Audit..."):
                try:
                    doctrine = """
                    SHREDLANE DOCTRINE:
                    - NO DASHES: Use bullet points (•) only.
                    - FATS: Must be in GRAMS. Reject 'ml' or 'spoons'.
                    - PROTEIN: Soy Chunks (100g)=50g, Chicken Breast (100g)=23g, Beef (100g)=20g, Eggs (1)=6g.
                    - REJECT generic 'chicken'. Require specific pieces.
                    - Tone: Professional, firm, Grade 7 English.
                    """
                    prompt = f"{doctrine}\n\nAudit for {client_name}:\n{whatsapp_data}\n{diary_log}"
                    
                    response = model.generate_content(prompt)
                    st.subheader(f"Audit for {client_name}")
                    st.markdown(response.text.replace("- ", "• "))
                    
                    # Sheets Sync
                    sheet = get_sheet()
                    if sheet:
                        w_match = re.search(r"Weight:\s*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                        weight = w_match.group(1) if w_match else "N/A"
                        sheet.append_row([str(date_today), client_name, weight])
                        st.toast("✅ Sheet Updated")
                except Exception as e:
                    st.error(f"Audit Error: {e}")

# --- 5. MEAL BUILDER ---
elif mode == "Meal Builder":
    st.header("🛠 Shredlane Meal Builder")
    u_weight = st.text_input("Client Weight (kg)")
    u_ingredients = st.text_area("Available Ingredients (Specify meat cuts!)")
    
    if st.button("Build Plan"):
        if not u_weight or not u_ingredients:
            st.error("Weight and Ingredients required.")
        else:
            with st.spinner("Generating..."):
                try:
                    res = model.generate_content(f"Shredlane Meal Plan (2 options, no dashes, fats in grams): {u_weight}kg, {u_ingredients}")
                    st.markdown(res.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Meal Builder Error: {e}")
