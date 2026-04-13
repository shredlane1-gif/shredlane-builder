import streamlit as st
from google import genai
from google.genai import types
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="Shredlane Prime", layout="wide")
st.title("⚡ Shredlane Prime: 2026 Automation")

api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account")

# Initialize Client
client = None
active_model = "gemini-3-flash" # Default target

if api_key:
    try:
        # 2026 SDK uses the Client object
        client = genai.Client(api_key=api_key)
        
        # SIDEBAR DIAGNOSTICS: See what you actually own
        with st.sidebar.expander("📡 API Model Discovery"):
            available_models = [m.name for m in client.models.list()]
            st.write(available_models)
            
            # Auto-select best available
            if "models/gemini-3-flash" in available_models:
                active_model = "gemini-3-flash"
            elif "models/gemini-2.5-flash" in available_models:
                active_model = "gemini-2.5-flash"
        
        st.sidebar.success(f"✅ Online: {active_model}")
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

# --- 3. AUDIT ENGINE ---
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
    
    if st.button("🚀 Run Shredlane Audit"):
        if not client and not api_key:
            st.error("AI Client not initialized.")
        elif "chicken" in diary_log.lower() and not any(cut in diary_log.lower() for cut in ["breast", "thigh", "wing", "drumstick", "leg"]):
            st.error("⚠️ SHREDLANE DOCTRINE: Specify chicken cut (Breast/Thigh) and weigh bone-free.")
        elif not client_name or not whatsapp_data:
            st.error("Missing Client Name or WhatsApp data.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    prompt = f"""
                    SYSTEM: Shredlane Auditor. 
                    RULES: Bullet points (•) only. NO DASHES. Fats in GRAMS. 
                    Reject generic chicken. Protein: Soy=50g/100g, Breast=23g/100g.
                    
                    INPUT: {client_name} | {targets} | {whatsapp_data} | {diary_log}
                    """
                    # New SDK call format
                    response = client.models.generate_content(
                        model=active_model,
                        contents=prompt
                    )
                    
                    st.subheader(f"Results: {client_name}")
                    clean_output = response.text.replace("- ", "• ").replace("—", "")
                    st.markdown(clean_output)
                    st.code(clean_output, language="markdown")
                    
                except Exception as e:
                    st.error(f"Audit Crash: {e}")

# --- 4. MEAL BUILDER ---
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
