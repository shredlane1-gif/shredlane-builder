import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Shredlane Prime", layout="wide")
st.title("💪 Shredlane Prime Master Control")

# Retrieve API Key from Streamlit Secrets
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found. Please set GOOGLE_API_KEY in your Streamlit secrets.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")

    # --- 2. MASTER SWITCH (The Radio Button) ---
    mode = st.radio("Select Mode:", ["Meal Builder", "Audit Engine"])

    # --- 3. MODE 1: MEAL BUILDER ---
    if mode == "Meal Builder":
        st.subheader("🛠 Meal Builder")
        gender = st.selectbox("Select Gender:", ["Female", "Male"])
        weight = st.text_input("Weight (kg):")
        ingredients = st.text_area("Ingredients:")

        if st.button("Build Plan"):
            # PASTE YOUR EXISTING MEAL BUILDER LOGIC BELOW
            shredlane_logic = r"""
            [PASTE YOUR PREVIOUS MEAL BUILDER PROMPT HERE]
            """
            full_prompt = f"System: {shredlane_logic}\n\nInput: Gender: {gender}, Weight: {weight}kg, Ingredients: {ingredients}"
            
            with st.spinner("Building your plan..."):
                response = model.generate_content(full_prompt)
                st.write(response.text)

    # --- 4. MODE 2: AUDIT ENGINE ---
    elif mode == "Audit Engine":
        st.subheader("📋 Shredlane Audit Engine")
        
        # Simple security for your Audit Engine
        password = st.text_input("Master Password:", type="password")
        if password != st.secrets.get("MASTER_PASSWORD", "SHREDLANE2026"):
            st.warning("Password required to access coaching tools.")
            st.stop()

        with st.form("audit_form"):
            client_name = st.text_input("Client Name")
            targets = st.text_input("Daily Targets (e.g., 1200 kcal / 90g Pro)")
            whatsapp_data = st.text_area("WhatsApp Check-in (Steps, Weight, Sleep, Water)")
            diary_log = st.text_area("MyNetDiary Log")
            submit_audit = st.form_submit_button("Generate Feedback")

        if submit_audit:
            doctrine_prompt = f"""
            YOU ARE THE SHREDLANE COACH. FOLLOW THE SHREDLANE DOCTRINE:
            1. NO DASHES (-) OR (—) ALLOWED.
            2. TONE: Concise, direct, diplomatic, WhatsApp-friendly.
            3. STRUCTURE: Status Header (✅/⚠️/❌), Key Metrics, Trend Tracking, Tomorrow Action Plan, Notes.
            4. NON-NEGOTIABLES: Reject generic 'Chicken/Stew'. Enforce precision.
            
            INPUTS:
            Client: {client_name}
            Targets: {targets}
            WhatsApp Data: {whatsapp_data}
            MyNetDiary Log: {diary_log}
            """
            with st.spinner("Analyzing data..."):
                response = model.generate_content(doctrine_prompt)
                # Ensure no dashes exist in final output
                feedback = response.text.replace("-", "").replace("—", "")
                st.write(feedback)
                st.code(feedback, language="markdown")
