import streamlit as st
import google.generativeai as genai
import gspread
from google.oauth2.service_account import Credentials
import re
from datetime import datetime

# --- 1. CONFIGURATION & SETUP ---
st.set_page_config(page_title="Shredlane Prime Master", layout="wide")

# Load Secrets
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
sheet_id = st.secrets.get("SPREADSHEET_ID")
google_creds = st.secrets.get("gcp_service_account") 

# Sidebar Status
st.sidebar.title("Navigation")
if api_key:
    st.sidebar.success("✅ API Key detected")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3-flash")
else:
    st.sidebar.error("❌ API Key NOT detected")

# --- 2. ACCESS CONTROL ---
# We define these FIRST so they are always available to the code
mode = st.sidebar.radio("Go to:", ["Audit Engine", "Meal Builder"])
password = st.sidebar.text_input("Master Password", type="password")

# This "Stop" ensures nothing below shows unless the password is correct
if not password:
    st.warning("🗝️ Please enter the Master Password in the sidebar to begin.")
    st.stop()

if password != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
    st.error("❌ Incorrect Password.")
    st.stop()

# --- 3. AUDIT ENGINE ---
if mode == "Audit Engine":
    st.header("📋 Shredlane Data Auditor")
    
    # We use a standard layout instead of a form first to see if it renders
    client_name = st.text_input("Client Name")
    targets = st.text_input("Daily Targets (e.g. 1500 kcal / 120g Pro)")
    date_today = st.date_input("Check-in Date", datetime.now())
    
    whatsapp_data = st.text_area("Paste WhatsApp Check-in Text:", height=150)
    diary_log = st.text_area("Paste MyNetDiary Log:", height=150)
    
    if st.button("🚀 Run Shredlane Audit"):
        if not client_name or not whatsapp_data:
            st.error("Please fill in the Client Name and WhatsApp data.")
        else:
            with st.spinner("Gemini 3 Flash is auditing..."):
                try:
                    prompt = f"Audit for {client_name}. Doctrine: No dashes, fats in grams. Input: {whatsapp_data} {diary_log}"
                    response = model.generate_content(prompt)
                    st.success("Audit Results:")
                    st.markdown(response.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Error: {e}")

# --- 4. MEAL BUILDER ---
elif mode == "Meal Builder":
    st.header("🛠 Shredlane Meal Builder")
    u_weight = st.text_input("Current Weight (kg)")
    u_ingredients = st.text_area("Available Ingredients")
    
    if st.button("Generate Plan"):
        with st.spinner("Building..."):
            res = model.generate_content(f"Shredlane Plan for {u_weight}kg: {u_ingredients}")
            st.markdown(res.text.replace("- ", "• "))
