import streamlit as st
from google import genai
import re
from datetime import datetime

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Shredlane Prime", layout="wide", page_icon="⚡")
st.title("⚡ Shredlane Prime: Doctrine-Locked")

# Accessing Secrets
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()

# Initialize Client & Stable Model Detection
client = None
active_model = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        
        # Priority: Gemini 3 Flash is the 2026 stable-speed standard.
        # Gemini 2.5 Flash is the backup for high-volume reasoning.
        priority_models = ["gemini-3-flash-preview", "gemini-2.5-flash"]
        
        available_models = [m.name for m in client.models.list()]
        for model_id in priority_models:
            # Check for the model with and without 'models/' prefix
            if any(model_id in name for name in available_models):
                active_model = model_id
                break
        
        if active_model:
            st.sidebar.success(f"✅ Doctrine Online: {active_model}")
        else:
            st.sidebar.error("❌ No supported models found. Check AI Studio.")
    except Exception as e:
        st.sidebar.error(f"⚠️ Connection Failed: {e}")

# Navigation
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])

# --- 2. THE SHREDLANE DOCTRINE ---
SHREDLANE_DOCTRINE = """
SHREDLANE DOCTRINE RULES (ENFORCE STRICTLY):
1. MEASUREMENTS: Everything must be in grams (g). Use of 'handful', 'portion', 'bowl', or 'piece' is a violation.
2. PROTEIN FLOOR: Target 1.6g - 2.0g protein per kg of bodyweight. 
3. SPECIFICITY: 'Chicken' is forbidden. Must specify cut (e.g., Breast, Thigh) and specify bone-free.
4. FATS: Ghee/Oil must be measured (e.g., 5g). No 'drizzling' or 'cooking with'.
5. SOY CONVERSION: 100g Soy Chunks = 50g Protein. 
6. FORMATTING: Use Bullet Points (•) ONLY. Never use dashes (-).
7. TONE: Firm, Professional, Grade 7 English. No fluff.
"""

# --- 3. AUDIT ENGINE ---
if mode == "Audit Engine":
    st.header("📋 Client Audit Engine")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name")
        targets = st.text_input("Daily Targets (e.g., 1800kcal)")
    with col2:
        date_today = st.date_input("Check-in Date", datetime.now())
        gender = st.selectbox("Gender", ["Female", "Male"])
    
    raw_data = st.text_area("Paste Client Data (WhatsApp/MyNetDiary):", height=200)
    
    if st.button("🚀 Run Doctrine Audit"):
        if not client_name or not raw_data:
            st.error("Missing Client Name or Data.")
        else:
            with st.spinner("Analyzing against Doctrine..."):
                try:
                    prompt = f"""
                    {SHREDLANE_DOCTRINE}
                    
                    TASK: Audit this {gender} client ({client_name}).
                    TARGETS: {targets}
                    DATA: {raw_data}
                    
                    Identify violations. If they are 'doing fine', state it, but highlight where they must be stricter.
                    """
                    response = client.models.generate_content(model=active_model, contents=prompt)
                    # Force the dot formatting
                    st.markdown(response.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Audit Crash: {e}")

# --- 4. MEAL BUILDER ---
elif mode == "Meal Builder":
    st.header("🛠 Doctrine Meal Builder")
    u_w = st.text_input("Client Weight (kg)")
    u_g = st.selectbox("Gender", ["Female", "Male"])
    u_i = st.text_area("Available Ingredients:")
    
    if st.button("🏗️ Build Plan"):
        if not u_w or not u_i:
            st.error("Weight and Ingredients required.")
        else:
            with st.spinner("Generating Shredlane Plan..."):
                try:
                    builder_prompt = f"""
                    {SHREDLANE_DOCTRINE}
                    
                    TASK: Build 2 daily meal plan options for a {u_w}kg {u_g}.
                    INGREDIENTS: {u_i}
                    
                    REQUIREMENTS: 
                    - Show the Protein Floor calculation.
                    - List every item in exact grams.
                    """
                    res = client.models.generate_content(model=active_model, contents=builder_prompt)
                    st.markdown(res.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Builder Error: {e}")
