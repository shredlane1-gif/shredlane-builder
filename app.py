import streamlit as st
from google import genai
import re
from datetime import datetime

# --- SETUP & THEME ---
st.set_page_config(page_title="Shredlane Prime", layout="wide", page_icon="⚡")
st.title("⚡ Shredlane Prime: Max-Token Edition")

# Connection Logic
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
client = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        # Using 2.5 Flash-Lite for the highest possible free tier quota (1000 RPD)
        active_model = "gemini-2.5-flash-lite"
        st.sidebar.success(f"🚀 High-Quota Mode: {active_model}")
    except Exception as e:
        st.sidebar.error(f"Connection Failed: {e}")

# Navigation
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])
user_pass = st.sidebar.text_input("Master Password", type="password")

if not user_pass:
    st.info("🗝️ Please enter your password to unlock the Shredlane Hub.")
    st.stop()

if user_pass != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
    st.error("❌ Incorrect Password.")
    st.stop()

# --- AUDIT ENGINE ---
if mode == "Audit Engine":
    st.header("📋 High-Performance Audit Engine")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name")
        targets = st.text_input("Daily Targets (e.g., 1800kcal)")
    with col2:
        date_today = st.date_input("Check-in Date", datetime.now())
        gender = st.selectbox("Gender", ["Female", "Male"])
    
    raw_data = st.text_area("Paste Client WhatsApp/Diary Data:", height=200)
    
    if st.button("🚀 Run Audit"):
        # Shredlane Doctrine: Check for "Chicken" specificity
        if "chicken" in raw_data.lower() and not any(x in raw_data.lower() for x in ["breast", "thigh", "wing", "drumstick"]):
            st.warning("⚠️ Doctrine Violation: Ask the client to specify the chicken cut (e.g., Breast).")
        
        with st.spinner("Analyzing with Shredlane Protocol..."):
            try:
                prompt = f"""
                ROLE: Shredlane Auditor. Firm tone. Grade 7 English.
                CLIENT: {client_name} ({gender}) | Targets: {targets}
                DATA: {raw_data}
                
                REQUIREMENTS:
                - Use bullet points (•). No dashes.
                - Analyze protein accuracy (Breast=23g/100g, Soy=50g/100g).
                - Highlight consistency trends.
                """
                response = client.models.generate_content(model=active_model, contents=prompt)
                st.markdown(response.text.replace("- ", "• "))
            except Exception as e:
                if "429" in str(e):
                    st.error("🚨 QUOTA FULL: Flash-Lite limit reached. Wait 60s or try tomorrow at 10 AM.")
                else:
                    st.error(f"Audit Error: {e}")

# --- MEAL BUILDER ---
elif mode == "Meal Builder":
    st.header("🛠 High-Token Meal Builder")
    u_w = st.text_input("Weight (kg)")
    u_g = st.selectbox("Gender", ["Female", "Male"])
    u_i = st.text_area("Ingredients Available:")
    
    if st.button("🏗️ Build Plan"):
        with st.spinner("Calculating macros..."):
            try:
                res = client.models.generate_content(
                    model=active_model, 
                    contents=f"Build a Shredlane meal plan for a {u_w}kg {u_g} using {u_i}. 2 options. • bullets only."
                )
                st.markdown(res.text.replace("- ", "• "))
            except Exception as e:
                st.error(f"Builder Error: {e}")
