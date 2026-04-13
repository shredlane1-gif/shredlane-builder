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
api_key = st.secrets.get("GOOGLE_API_KEY")
sheet_id = st.secrets.get("SPREADSHEET_ID")
# Google Service Account info should be stored as a dict in secrets
google_creds = st.secrets.get("gcp_service_account") 

# Initialize Gemini
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")

# Initialize Google Sheets Connection
def get_sheet():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(google_creds, scopes=scopes)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id).sheet1

# --- 2. HELPER FUNCTIONS ---
def extract_metrics(text):
    """Extracts numbers from the WhatsApp check-in format."""
    metrics = {
        "weight": re.search(r"Weight:\s*(\d+\.?\d*)", text),
        "waist": re.search(r"Waist:\s*(\d+\.?\d*)", text),
        "steps": re.search(r"Steps:\s*(\d+)", text),
        "sleep": re.search(r"Sleep:\s*(\d+)", text), # Simplistic hours extraction
    }
    return {k: (v.group(1) if v else "Not reported") for k, v in metrics.items()}

# --- 3. NAVIGATION ---
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])

if mode == "Audit Engine":
    st.subheader("📋 Shredlane Data Auditor")
    
    # Master Password Check
    password = st.sidebar.text_input("Master Password", type="password")
    if password != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
        st.warning("Please enter the Master Password in the sidebar.")
        st.stop()

    with st.form("audit_form"):
        col1, col2 = st.columns(2)
        with col1:
            client_name = st.text_input("Client Name (Must match Sheet exactly)")
            targets = st.text_input("Daily Targets (e.g., 1200 kcal / 90g Pro)")
        with col2:
            date_today = st.date_input("Check-in Date", datetime.now())
        
        whatsapp_data = st.text_area("Paste WhatsApp Check-in Here:")
        diary_log = st.text_area("Paste MyNetDiary Log Here:")
        
        submit_audit = st.form_submit_button("Generate Audit & Sync Data")

    if submit_audit:
        # 1. Extraction Logic
        metrics = extract_metrics(whatsapp_data)
        
        # 2. Shredlane Doctrine Prompt
        doctrine_prompt = f"""
        You are the Shredlane Data Auditor. Adhere to SHREDLANE DOCTRINE.
        
        STRICT PROTEIN TABLE:
        - Soy Chunks (100g) = 50g | Chicken Breast (100g) = 23g | Beef/Goat (100g) = 20g
        - Eggs (1) = 6g | Lentils/Beans (100g cooked) = 9g | Greek Yogurt (100g) = 10g
        - Cooked Ugali (100g) = 3g
        
        RULES:
        - Fats strictly in GRAMS. Warn if 'ml' or 'spoons' is used.
        - NO DASHES in output.
        - Tone: Professional, direct, Grade 7 level.
        
        INPUTS:
        Client: {client_name} | Targets: {targets}
        Data: {whatsapp_data} {diary_log}
        """

        with st.spinner("Auditing data..."):
            # Generate AI Feedback
            response = model.generate_content(doctrine_prompt)
            final_feedback = response.text.replace("- ", "").replace("—", "")
            
            # Display Feedback
            st.success("Audit Complete")
            st.markdown(final_feedback)
            st.code(final_feedback, language="markdown")

            # 3. SYNC TO GOOGLE SHEETS
            try:
                sheet = get_sheet()
                # Prepare row: Date, Name, Weight, Waist, Steps, Sleep
                new_row = [
                    str(date_today), 
                    client_name, 
                    metrics["weight"], 
                    metrics["waist"], 
                    metrics["steps"], 
                    metrics["sleep"]
                ]
                sheet.append_row(new_row)
                st.info(f"✅ Data synced to Google Sheet for {client_name}")
            except Exception as e:
                st.error(f"Failed to sync to Sheets: {e}")

elif mode == "Meal Builder":
    st.subheader("🛠 Shredlane Meal Builder")
    # (Keeping your existing meal builder logic here, ensuring no dashes are used)
    gender = st.selectbox("Gender", ["Female", "Male"])
    weight = st.text_input("Weight (kg)")
    ingredients = st.text_area("Available Ingredients")

    if st.button("Build Plan"):
        meal_prompt = f"System: Shredlane Meal Builder. Fats 20-30%. No flour (use Cooked Ugali). Fats in GRAMS. Format: Option 1 (2 meals), Option 2 (1 big meal). No dashes.\n\nInput: {gender}, {weight}kg, {ingredients}"
        with st.spinner("Building..."):
            res = model.generate_content(meal_prompt)
            st.write(res.text)
