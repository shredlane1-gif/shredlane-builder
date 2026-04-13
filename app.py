import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Shredlane Prime Master", layout="wide")
st.title("⚡ Shredlane Prime: Automation Hub")

# Load Secrets from Streamlit
api_key = st.secrets.get("GOOGLE_API_KEY")
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account") 

# Initialize Gemini Model
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

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

# --- 2. HELPER FUNCTIONS ---
def extract_metrics(text):
    """Automatically pulls numbers from the WhatsApp check-in text."""
    metrics = {
        "weight": re.search(r"Weight:\s*(\d+\.?\d*)", text, re.IGNORECASE),
        "waist": re.search(r"Waist:\s*(\d+\.?\d*)", text, re.IGNORECASE),
        "steps": re.search(r"Steps:\s*(\d+)", text, re.IGNORECASE),
        "sleep": re.search(r"Sleep:\s*(\d+)", text, re.IGNORECASE),
    }
    return {k: (v.group(1) if v else "Not reported") for k, v in metrics.items()}

# --- 3. NAVIGATION & ACCESS CONTROL ---
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])

# PASSWORD CHECK
password = st.sidebar.text_input("Master Password", type="password")

if not password:
    st.info("🗝️ Enter the Master Password in the sidebar to unlock the system.")
    st.stop()

correct_password = st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026")
if password != correct_password:
    st.error("❌ Incorrect Password. Access Denied.")
    st.stop()

# --- 4. MODE: AUDIT ENGINE ---
if mode == "Audit Engine":
    st.subheader("📋 Shredlane Data Auditor")
    
    # Everything inside this 'with' block belongs to the form
    with st.form("audit_form"):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Client Name")
            targets = st.text_input("Daily Targets (e.g., 1500 kcal / 120g Pro)")
        with col2:
            date_today = st.date_input("Check-in Date", datetime.now())
        
        whatsapp_data = st.text_area("Paste WhatsApp Check-in Here:")
        diary_log = st.text_area("Paste MyNetDiary Log Here:")
        
        # This button MUST be indented inside the 'with st.form' block
        submit_audit = st.form_submit_button("Generate Audit & Sync Data")

    # This logic runs AFTER the form is submitted
    if submit_audit:
        metrics = extract_metrics(whatsapp_data)
        
        doctrine_prompt = f"""
        You are the Shredlane Data Auditor. Adhere strictly to the Shredlane Doctrine.
        
        STRICT PROTEIN TABLE:
        Soy Chunks (100g) = 50g | Chicken Breast (100g) = 23g | Beef/Goat (100g) = 20g
        Eggs (1 unit) = 6g | Lentils/Beans (100g cooked) = 9g | Greek Yogurt (100g) = 10g
        Cooked Ugali (100g) = 3g.
        
        MANDATORY RULES:
        1. Fats MUST be in GRAMS. Warn if 'ml' or 'spoons' is used.
        2. NEVER use dashes (-) or (—) in the output. Use bullet points or numbers.
        3. Tone: Professional, firm, but kind. Grade 7 level language.
        
        INPUT DATA:
        Client: {client_name} | Targets: {targets}
        Stats: {whatsapp_data} | Logs: {diary_log}
        """

        with st.spinner("Processing..."):
            response = model.generate_content(doctrine_prompt)
            final_feedback = response.text.replace("- ", "• ").replace("—", "")
            
            st.success("Audit Complete")
            st.markdown(final_feedback)
            st.code(final_feedback, language="markdown")

            # Sync to Sheets
            sheet = get_sheet()
            if sheet:
                try:
                    new_row = [str(date_today), client_name, metrics["weight"], metrics["waist"], metrics["steps"], metrics["sleep"]]
                    sheet.append_row(new_row)
                    st.toast(f"✅ Logged to Sheets for {client_name}!")
                except Exception as e:
                    st.error(f"Sheet Sync Error: {e}")

# --- 5. MODE: MEAL BUILDER ---
elif mode == "Meal Builder":
    st.subheader("🛠 Shredlane Meal Builder")
    
    with st.form("meal_form"):
        col1, col2 = st.columns(2)
        with col1:
            gender = st.selectbox("Gender", ["Female", "Male"])
            weight = st.text_input("Current Weight (kg)")
        with col2:
            ingredients = st.text_area("Available Ingredients")

        submit_meal = st.form_submit_button("Build Shredlane Plan")

    if submit_meal:
        if not weight or not ingredients:
            st.warning("Please enter weight and ingredients.")
        else:
            meal_logic = "Shredlane Meal Builder: Fats 20-30%. No flour (use Cooked Ugali). Fats in GRAMS. No dashes. Option 1 (2 meals), Option 2 (1 big meal)."
            full_prompt = f"{meal_logic}\n\nInput: {gender}, {weight}kg, {ingredients}"
            
            with st.spinner("Building..."):
                res = model.generate_content(full_prompt)
                st.markdown(res.text.replace("- ", "• "))
