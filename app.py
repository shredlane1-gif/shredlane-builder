import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Shredlane Prime", layout="wide")
st.title("💪 Shredlane Prime Master Control")

api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found. Please set GOOGLE_API_KEY in your Streamlit secrets.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")

    mode = st.radio("Select Mode:", ["Meal Builder", "Audit Engine"])

    # --- 3. MODE 1: MEAL BUILDER ---
    if mode == "Meal Builder":
        st.subheader("🛠 Meal Builder")
        gender = st.selectbox("Select Gender:", ["Female", "Male"])
        weight = st.text_input("Weight (kg):")
        ingredients = st.text_area("Ingredients:")

        if st.button("Build Plan"):
            # UPDATED LOGIC TO FIX EGG MEASUREMENTS
            shredlane_logic = r"""
            You are the Shredlane Meal Builder. 
            STRICT RULES:
            1. UNITS: Always use 'whole units' for Eggs (e.g., 1 egg, 2 eggs). NEVER use grams for eggs.
            2. WEIGHT: Use grams (raw weight) for meats and grains.
            3. FORMAT: List each ingredient with its clear portion size.
            4. TONE: Direct, simple, and action-oriented.
            """
            full_prompt = f"System: {shredlane_logic}\n\nInput: Gender: {gender}, Weight: {weight}kg, Ingredients: {ingredients}"
            
            with st.spinner("Building your plan..."):
                response = model.generate_content(full_prompt)
                st.write(response.text)

    # --- 4. MODE 2: AUDIT ENGINE ---
    elif mode == "Audit Engine":
        st.subheader("📋 Shredlane Audit Engine")
        
        password = st.text_input("Master Password:", type="password")
        if password != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
            st.warning("Password required.")
            st.stop()

        with st.form("audit_form"):
            client_name = st.text_input("Client Name")
            targets = st.text_input("Daily Targets (e.g., 1200 kcal / 90g Pro)")
            whatsapp_data = st.text_area("WhatsApp Check-in (Steps, Weight, Sleep, Water)")
            diary_log = st.text_area("MyNetDiary Log")
            submit_audit = st.form_submit_button("Generate Feedback")

        if submit_audit:
            doctrine_prompt = f"""
            You are the Shredlane Data Auditor. Use this reference for protein:
            - Chicken Breast (100g) = 23g, Eggs (1 unit) = 6g, Greek Yogurt (100g) = 10g, Beef/Goat (100g) = 20g, Beans/Lentils (100g) = 9g.
            
            STRICT RULES:
            1. If log says '1 egg', calculate as 6g protein.
            2. VERIFICATION: Calculate totals only from log. If unreadable, report 'Log data incomplete'.
            3. NO DASHES: Do not use '-' or '—'.
            4. STRUCTURE: Status, Numbers, Progress, Plan, Coach's Note.
            
            INPUTS:
            Client: {client_name}, Targets: {targets}, Data: {whatsapp_data}, Log: {diary_log}
            """
            
            with st.spinner("Analyzing data..."):
                response = model.generate_content(doctrine_prompt)
                final_feedback = response.text.replace("-", "").replace("—", "")
                st.write(final_feedback)
                st.code(final_feedback, language="markdown")
