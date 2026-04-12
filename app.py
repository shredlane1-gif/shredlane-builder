import streamlit as st
import google.generativeai as genai

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Shredlane Prime", layout="wide")
st.title("💪 Shredlane Prime Master Control")

# Retrieve API Key
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found. Please set GOOGLE_API_KEY in your Streamlit secrets.")
else:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3-flash-preview")

    # --- 2. MASTER SWITCH ---
    mode = st.radio("Select Mode:", ["Meal Builder", "Audit Engine"])

    # --- 3. MODE 1: MEAL BUILDER ---
    if mode == "Meal Builder":
        st.subheader("🛠 Meal Builder")
        gender = st.selectbox("Select Gender:", ["Female", "Male"])
        weight = st.text_input("Weight (kg):")
        ingredients = st.text_area("Ingredients:")

        if st.button("Build Plan"):
            shredlane_logic = r"""
            You are the Shredlane Meal Builder. You create high-precision meal plans for the Kenyan market.
            
            STRICT MACRONUTRIENT RULES:
            - FATS: Must be strictly between 20% and 30% of total calories.
            - PROTEIN: Prioritize high protein based on the user's weight.
            
            STRICT MEASUREMENT & FOOD RULES:
            1. EGGS: Always use 'whole units' (e.g., 2 eggs). NEVER use grams for eggs.
            2. NO FLOUR: Do not list 'Maize Flour' or 'Ugali Flour'. Use 'Cooked Ugali' measured in grams.
            3. MEATS/SIDES: Use grams (cooked weight for ugali, raw weight for proteins).
            4. FATS: Use grams or teaspoons for Ghee/Oil.
            
            REQUIRED OUTPUT FORMAT:
            You must provide exactly two options:
            
            OPTION 1: TWO MEALS (Split the ingredients into two separate sittings)
            - Meal 1: [Ingredients and portions]
            - Meal 2: [Ingredients and portions]
            
            OPTION 2: ONE BIG MEAL (Combine all ingredients into one large sitting)
            - Meal: [All ingredients and portions]
            
            TONE: Direct, simple, and professional.
            """
            full_prompt = f"System: {shredlane_logic}\n\nInput: Gender: {gender}, Weight: {weight}kg, Ingredients: {ingredients}"
            
            with st.spinner("Calculating macros and building options..."):
                response = model.generate_content(full_prompt)
                st.write(response.text)

    # --- 4. MODE 2: AUDIT ENGINE ---
    elif mode == "Audit Engine":
        st.subheader("📋 Shredlane Audit Engine")
        
        # Security
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
            You are the Shredlane Data Auditor. Use this reference for protein calculation:
            - Chicken Breast (100g) = 23g
            - Eggs (1 unit) = 6g
            - Greek Yogurt (100g) = 10g
            - Beef/Goat (100g) = 20g
            - Beans/Lentils (100g) = 9g
            - Cooked Ugali (100g) = 3g
            
            STRICT DATA RULES:
            1. PROTEIN: Sum the values from the MyNetDiary log using the table above.
            2. VERIFICATION: If info is missing, write 'Not reported'. Do not guess.
            3. FORMATTING: Do NOT use any dashes (-) or (—). 
            4. STRUCTURE: Status (✅/⚠️/❌), Numbers, Your Progress, Tomorrow's Plan, Coach's Note.
            
            INPUTS:
            Client: {client_name}
            Targets: {targets}
            WhatsApp Data: {whatsapp_data}
            MyNetDiary Log: {diary_log}
            """
            
            with st.spinner("Analyzing data and calculating protein..."):
                response = model.generate_content(doctrine_prompt)
                # Final cleanup: Strip all dashes
                final_feedback = response.text.replace("-", "").replace("—", "")
                st.write(final_feedback)
                st.code(final_feedback, language="markdown")
