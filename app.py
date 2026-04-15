import streamlit as st
from google import genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. INITIAL SETUP & THEME ---
st.set_page_config(page_title="Shredlane Prime", layout="wide", page_icon="⚡")

# Custom CSS for a cleaner look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #000; color: #fff; }
    .stTextArea>div>div>textarea { border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚡ Shredlane Prime: Automation Hub")

# Accessing Credentials
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account")

# Initialize AI Client & Auto-Detect Model
client = None
active_model = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        available_models = [m.name for m in client.models.list()]
        
        # Priority: Try 2.0 first, fallback to 1.5 if 2.0 quota is full
        priority_names = ["models/gemini-2.0-flash", "models/gemini-1.5-flash"]
        
        for name in priority_names:
            if name in available_models:
                active_model = name
                break
        
        if active_model:
            st.sidebar.success(f"✅ AI Online: {active_model}")
        else:
            st.sidebar.error("❌ No models found. Check API Key.")
    except Exception as e:
        st.sidebar.error(f"Connection Failed: {e}")

# --- 2. SIDEBAR NAVIGATION & SECURITY ---
st.sidebar.header("Control Center")
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])
user_pass = st.sidebar.text_input("Master Password", type="password")

# Block access until password is correct
if not user_pass:
    st.info("🗝️ Enter password to unlock system.")
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
        
        # Security check for Name
        safe_name = str(name).strip() if name else "Unknown Client"
        
        # append_row ensures every audit is a NEW entry
        sheet.append_row([str(date), safe_name, weight, waist, steps], value_input_option="USER_ENTERED")
        return True
    except Exception as e:
        st.error(f"Sheet Sync Error: {e}")
        return False

# --- 4. AUDIT ENGINE MODE ---
if mode == "Audit Engine":
    st.header("📋 Client Audit Engine")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name", placeholder="e.g. Merceline")
        targets = st.text_input("Daily Targets", placeholder="e.g. 1800kcal, 120g Protein")
    with col2:
        date_today = st.date_input("Check-in Date", datetime.now())
        client_gender = st.selectbox("Client Gender", ["Female", "Male"])
    
    whatsapp_data = st.text_area("Paste WhatsApp Stats (Weight, Waist, Steps):", height=100)
    diary_log = st.text_area("Paste MyNetDiary Log:", height=150)
    
    if st.button("🚀 Run Audit & Sync"):
        # SHREDLANE DOCTRINE: The Chicken Rule
        if "chicken" in diary_log.lower() and not any(cut in diary_log.lower() for cut in ["breast", "thigh", "wing", "drumstick", "leg"]):
            st.error("⚠️ DOCTRINE VIOLATION: Specify the chicken piece (e.g. Breast) and weigh bone-free.")
        elif not client_name or not whatsapp_data:
            st.error("Missing Client Name or Stats.")
        else:
            with st.spinner("Analyzing data according to Shredlane Doctrine..."):
                try:
                    doctrine_prompt = f"""
                    ROLE: Shredlane Auditor. 
                    TONE: Professional, firm, Grade 7 English. No jargon.
                    CLIENT: {client_name} ({client_gender})
                    
                    RULES: 
                    - Use bullet points (•) only. NO DASHES.
                    - Protein standards: Soy Chunks (100g)=50g, Chicken Breast (100g)=23g, Beef (100g)=20g, Eggs (1)=6g, Fish (100g)=20g.
                    - If female, note that weight spikes may be hormonal (Cycle Week 4).
                    
                    AUDIT THIS: Targets: {targets} | Stats: {whatsapp_data} | Log: {diary_log}
                    """
                    response = client.models.generate_content(model=active_model, contents=doctrine_prompt)
                    
                    st.subheader(f"Audit Results: {client_name}")
                    # Remove any AI hallucinated dashes for clean bullet points
                    clean_output = response.text.replace("- ", "• ").replace("—", "")
                    st.markdown(clean_output)
                    
                    # FLEXIBLE EXTRACTION
                    w_match = re.search(r"(?:weight|wt|wgt)[:\s]*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                    wa_match = re.search(r"(?:waist|wst)[:\s]*(\d+\.?\d*)", whatsapp_data, re.IGNORECASE)
                    s_match = re.search(r"(?:steps|stp|st)[:\s]*(\d+)", whatsapp_data, re.IGNORECASE)
                    
                    w_val = w_match.group(1) if w_match else "N/A"
                    wa_val = wa_match.group(1) if wa_match else "N/A"
                    s_val = s_match.group(1) if s_match else "N/A"
                    
                    if sync_to_sheets(date_today, client_name, w_val, wa_val, s_val):
                        st.toast(f"✅ Logged {client_name} to Google Sheets!")
                        
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚨 QUOTA EXHAUSTED: Google is busy. Please wait 60 seconds.")
                    else:
                        st.error(f"Audit Crash: {e}")

# --- 5. MEAL BUILDER MODE ---
elif mode == "Meal Builder":
    st.header("🛠 Shredlane Meal Builder")
    
    col_a, col_b = st.columns(2)
    with col_a:
        u_weight = st.text_input("Weight (kg)")
    with col_b:
        u_gender = st.selectbox("Client Gender", ["Female", "Male"])
        
    u_ingredients = st.text_area("Available Ingredients (Be specific about cuts!)")
    
    if st.button("🏗️ Build Plan"):
        if not u_weight or not u_ingredients:
            st.warning("Provide weight and ingredients.")
        else:
            with st.spinner(f"Building balanced protocol for {u_gender}..."):
                try:
                    builder_prompt = f"""
                    ROLE: Shredlane Nutritionist.
                    TASK: Build a {u_gender} Meal Plan for a {u_weight}kg individual.
                    INGREDIENTS: {u_ingredients}
                    
                    RULES:
                    - Account for {u_gender} metabolic differences.
                    - Protein target: ~2g per kg of bodyweight.
                    - Provide TWO options. No dashes. Use bullet points (•).
                    - List fats in grams. Grade 7 English only.
                    """
                    res = client.models.generate_content(model=active_model, contents=builder_prompt)
                    st.markdown(res.text.replace("- ", "• "))
                except Exception as e:
                    if "429" in str(e):
                        st.error("🚨 QUOTA EXHAUSTED: Try again in 60 seconds.")
                    else:
                        st.error(f"Builder Error: {e}")
