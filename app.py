import streamlit as st
from google import genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="Shredlane Prime Hub", layout="wide")
st.title("⚡ Shredlane Prime: Automation Hub")import streamlit as st
from google import genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. SETUP & DOCTRINE ---
st.set_page_config(page_title="Shredlane Prime", layout="wide")
st.title("⚡ Shredlane Prime: Automation Hub")

api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account")

# Initialize Client
client = None
active_model = "gemini-3-flash" 

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        st.sidebar.success(f"✅ AI Online: Gemini 3 Flash")
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
            st.error("⚠️ SHREDLANE DOCTRINE: You must specify the chicken piece (e.g. Breast) and weigh it bone-free.")
        elif not client_name or not whatsapp_data:
            st.error("Missing Client Name or Stats.")
        else:
            with st.spinner("Auditing..."):
                try:
                    doctrine_prompt = f"""
                    ROLE: Shredlane Auditor. 
                    TONE: Professional, firm, Grade 7 English. Avoid jargon.
                    RULES: 
                    - Bullet points (•) only. NO DASHES.
                    - Fats: Must be in GRAMS. 
                    - Protein: Soy Chunks (100g)=50g, Chicken Breast (100g)=23g, Beef (100g)=20g, Eggs (1)=6g, Fish (100g)=20g.
                    - If a measurement is missing, just say: "Need grams for [Food Name] to calculate macros."
                    
                    AUDIT THIS: {client_name} | {targets} | {whatsapp_data} | {diary_log}
                    """
                    response = client.models.generate_content(model=active_model, contents=doctrine_prompt)
                    
                    # Display Results
                    st.subheader(f"Results for {client_name}")
                    clean_output = response.text.replace("- ", "• ").replace("—", "")
                    st.markdown(clean_output)
                    
                    # --- DATA EXTRACTION FOR SHEETS ---
                    weight = re.search(r"Weight:\s*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                    waist = re.search(r"Waist:\s*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                    steps = re.search(r"Steps:\s*(\d+)", whatsapp_data, re.IGNORECASE)
                    
                    w_val = weight.group(1) if weight else "N/A"
                    wa_val = waist.group(1) if waist else "N/A"
                    s_val = steps.group(1) if steps else "N/A"
                    
                    # Sync
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

api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account")

# Initialize Client & Model Discovery
client = None
active_model = "gemini-3-flash" # Targeted model

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        # Sidebar Diagnostic: Check which models are actually available to this key
        with st.sidebar.expander("📡 Model Discovery"):
            available_models = [m.name for m in client.models.list()]
            st.write(available_models)
            # Auto-fallback logic
            if "models/gemini-3-flash" not in available_models:
                active_model = "gemini-2.5-flash" if "models/gemini-2.5-flash" in available_models else "gemini-1.5-flash"
        
        st.sidebar.success(f"✅ AI Online: {active_model}")
    except Exception as e:
        st.sidebar.error(f"Connection Failed: {e}")

# --- 2. SECURITY ---
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])
user_pass = st.sidebar.text_input("Master Password", type="password")

if not user_pass:
    st.info("🗝️ Enter Master Password to unlock Shredlane tools.")
    st.stop()

if user_pass != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
    st.error("❌ Access Denied.")
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
    
    if st.button("🚀 Run Audit & Sync"):
        # REJECTION LOGIC for generic chicken
        if "chicken" in diary_log.lower() and not any(cut in diary_log.lower() for cut in ["breast", "thigh", "wing", "drumstick", "leg"]):
            st.error("⚠️ Shredlane Doctrine Violation: Generic 'chicken' detected. Specify the piece (e.g., Breast) and weigh without bones.")
        elif not client_name or not whatsapp_data:
            st.error("Missing required data fields.")
        else:
            with st.spinner("Analyzing..."):
                try:
                    doctrine = """
                    You are the Shredlane Auditor. 
                    - NO DASHES: Use bullet points (•) only.
                    - FATS: Must be in GRAMS.
                    - PROTEIN: Breast=23g/100g, Soy=50g/100g, Beef/Goat=20g/100g.
                    - TONE: Professional, firm, Grade 7 English.
                    """
                    response = client.models.generate_content(
                        model=active_model,
                        contents=f"{doctrine}\n\nAudit for {client_name}:\n{whatsapp_data}\n{diary_log}"
                    )
                    
                    st.subheader(f"Results for {client_name}")
                    clean_text = response.text.replace("- ", "• ").replace("—", "")
                    st.markdown(clean_text)
                    st.code(clean_text, language="markdown")
                    
                except Exception as e:
                    st.error(f"Audit Crash: {e}")

# --- 4. MEAL BUILDER ---
elif mode == "Meal Builder":
    st.header("🛠 Shredlane Meal Builder")
    u_weight = st.text_input("Weight (kg)")
    u_ingredients = st.text_area("Ingredients (Specify cuts!)")
    
    if st.button("Build Plan"):
        with st.spinner("Generating..."):
            try:
                res = client.models.generate_content(
                    model=active_model,
                    contents=f"Shredlane Meal Plan: {u_weight}kg, {u_ingredients}. Two options. No dashes. Fats in grams."
                )
                st.markdown(res.text.replace("- ", "• "))
            except Exception as e:
                st.error(f"Builder Error: {e}")
