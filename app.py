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
            shredlane_logic = r"""
            You are the Shredlane Meal Builder.
            RULES: 
            - Fats 20-30% of calories. 
            - Eggs in units. Meats/Grains in grams (raw). 
            - NO flour, use 'Cooked Ugali' in grams. 
            - Fats strictly in GRAMS.
            - Format: Option 1 (Two Meals), Option 2 (One Big Meal).
            """
            full_prompt = f"System: {shredlane_logic}\n\nInput: Gender: {gender}, Weight: {weight}kg, Ingredients: {ingredients}"
            with st.spinner("Building plan..."):
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
            whatsapp_data = st.text_area("WhatsApp Check-in")
            diary_log = st.text_area("MyNetDiary Log")
            submit_audit = st.form_submit_button("Generate Feedback")

        if submit_audit:
            # ENHANCED PROTEIN MAPPING
            doctrine_prompt = f"""
            You are the Shredlane Data Auditor. 
            
            STRICT PROTEIN CALCULATION TABLE:
            - Soy Protein Chunks (100g) = 50g protein
            - Chicken Breast (100g) = 23g protein
            - Beef/Goat (100g) = 20g protein
            - Eggs (1 large unit) = 6g protein
            - Lentils/Beans (100g cooked) = 9g protein
            - Greek Yogurt (100g) = 10g protein
            - Cooked Ugali (100g) = 3g protein
            
            MANDATORY CALCULATION RULES:
            1. DO NOT IGNORE PROTEIN. If a food item clearly contains protein (like Soy Chunks, Fish, or Meat) but isn't in the table above, you MUST use standard nutritional data to estimate it. Never report 0g for a protein source.
            2. SUM EVERYTHING: Add up every protein source to find the total.
            3. NO DASHES: Do not use '-' or '—'.
            4. FAT CHECK: Ensure Ghee/Oil is in GRAMS. If not, warn the client.
            5. STRUCTURE: Status, Numbers, Your Progress, Tomorrow's Plan, Coach's Note.

            INPUTS:
            Client: {client_name}
            Targets: {targets}
            WhatsApp Data: {whatsapp_data}
            MyNetDiary Log: {diary_log}
            """
            
            with st.spinner("Calculating total protein..."):
                response = model.generate_content(doctrine_prompt)
                final_feedback = response.text.replace("-", "").replace("—", "")
                st.write(final_feedback)
                st.code(final_feedback, language="markdown")
