import streamlit as st
from google import genai
import re
from datetime import datetime

# --- SETUP & THEME ---
st.set_page_config(page_title="Shredlane Prime", layout="wide", page_icon="⚡")
st.title("⚡ Shredlane Prime: Doctrine-Locked")

# Connection Logic
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
client = None

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        active_model = "gemini-1.5-flash"
        st.sidebar.success(f"🚀 System Online: {active_model}")
    except Exception as e:
        st.sidebar.error(f"Connection Failed: {e}")

# Navigation
mode = st.sidebar.radio("Navigation", ["Audit Engine", "Meal Builder"])

# --- DOCTRINE CONSTANTS ---
# This forces the AI to never deviate from your specific rules
SHREDLANE_RULES = """
SHREDLANE DOCTRINE RULES:
1. NO VAGUE TERMS: Never use 'handful', 'portion', 'some', or 'bowl'. 
2. EVERYTHING IN GRAMS: All food must be listed in grams (g).
3. PROTEIN FLOOR: Ensure a minimum of 1.6g to 2.0g of protein per kg of bodyweight.
4. CALORIE DENSITY: Limit fats (Ghee/Oil) to specific gram measurements (e.g., 5g or 10g). No 'drizzling'.
5. CHICKEN RULE: Always specify the cut (Breast, Thigh, etc.) and weigh bone-free.
6. SOY RULE: 100g Soy Chunks = 50g Protein.
7. FORMATTING: Use Bullet Points (•) ONLY. Never use dashes (-).
8. TONE: Firm, professional, Grade 7 English.
"""

# --- AUDIT ENGINE ---
if mode == "Audit Engine":
    st.header("📋 Doctrine Audit Engine")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Client Name")
        targets = st.text_input("Daily Targets (e.g., 1800kcal)")
    with col2:
        date_today = st.date_input("Check-in Date", datetime.now())
        gender = st.selectbox("Gender", ["Female", "Male"])
    
    raw_data = st.text_area("Paste Client WhatsApp/Diary Data:", height=200)
    
    if st.button("🚀 Run Doctrine Audit"):
        if not client_name or not raw_data:
            st.error("Please provide a name and client data.")
        else:
            with st.spinner("Enforcing Doctrine..."):
                try:
                    # The Forced Prompt
                    prompt = f"""
                    {SHREDLANE_RULES}
                    
                    TASK: Audit this {gender} client named {client_name}.
                    TARGETS: {targets}
                    DATA TO AUDIT: {raw_data}
                    
                    INSTRUCTION: Identify every violation of the doctrine. If they used 'handfuls', call it out. If they missed their protein floor, flag it.
                    """
                    response = client.models.generate_content(model=active_model, contents=prompt)
                    st.markdown(response.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Audit Error: {e}")

# --- MEAL BUILDER ---
elif mode == "Meal Builder":
    st.header("🛠 Doctrine Meal Builder")
    u_w = st.text_input("Weight (kg)")
    u_g = st.selectbox("Gender", ["Female", "Male"])
    u_i = st.text_area("Available Ingredients:")
    
    if st.button("🏗️ Build Plan"):
        if not u_w or not u_i:
            st.error("Weight and Ingredients required.")
        else:
            with st.spinner("Calculating Macros..."):
                try:
                    # The Forced Prompt
                    builder_prompt = f"""
                    {SHREDLANE_RULES}
                    
                    TASK: Build a daily meal plan for a {u_w}kg {u_g}.
                    AVAILABLE INGREDIENTS: {u_i}
                    
                    SPECIFICS:
                    - Calculate the total protein floor (Weight x 2).
                    - List exact grams for every ingredient.
                    - Provide 2 distinct options.
                    """
                    res = client.models.generate_content(model=active_model, contents=builder_prompt)
                    st.markdown(res.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Builder Error: {e}")
