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
            [PASTE YOUR PREVIOUS MEAL BUILDER PROMPT HERE]
            """
            full_prompt = f"System: {shredlane_logic}\n\nInput: Gender: {gender}, Weight: {weight}kg, Ingredients: {ingredients}"
            
            with st.spinner("Building your plan..."):
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
            # THIS IS THE FINAL DATA-RELIABLE PROMPT WITH PROTEIN CALCULATION
            doctrine_prompt = f"""
            You are the Shredlane Data Auditor. Your task is to provide daily coaching feedback based ONLY on provided data.
            
            STRICT DATA RULES:
            1. PROTEIN CALCULATION: Use this reference table for the MyNetDiary Log to calculate total protein:
               - Chicken Breast (100g) = 23g protein
               - Eggs (1 large) = 6g protein
               - Greek Yogurt (100g) = 10g protein
               - Beef/Goat (100g) = 20g protein
               - Beans/Lentils (100g) = 9g protein
               - If an item is missing from this list, estimate based on standard data.
               Sum these values for the total. If the log entry is just 'Chicken', assume 100g.
            
            2. VERIFICATION: Calculate totals only from the 'MyNetDiary Log' provided. Do not guess. If the log is completely unreadable, report it as 'Log data incomplete'.
            
            3. GRADE 7 LEVEL: Write in simple, easy English. No complex business jargon.
            
            4. FORMATTING: Do NOT use any dashes (-) or (—) in your output. Use numbers or plain text.
            
            5. STRUCTURE:
               STATUS: (Use ✅ for Good, ⚠️ for Warning, ❌ for Bad)
               
               NUMBERS:
               Calories: [Total kcal from log]
               Protein: [Calculated Total]g
               Steps: [From check-in]
               Sleep: [From check-in]
               
               YOUR PROGRESS:
               [Briefly mention weight and waist trend based on check-in]
               
               TOMORROW'S PLAN:
               1. [Instruction 1]
               2. [Instruction 2]
               3. [Instruction 3]
               
               COACH'S NOTE:
               [2 to 3 simple sentences. Be kind, firm, and focus on the rules.]

            THE RULES TO ENFORCE:
            - Always require weighing food before cooking.
            - If steps are below 7,000, explicitly tell them to walk more.

            INPUTS:
            Client: {client_name}
            Targets: {targets}
            WhatsApp Data: {whatsapp_data}
            MyNetDiary Log: {diary_log}
            """
            
            with st.spinner("Analyzing data and calculating protein..."):
                response = model.generate_content(doctrine_prompt)
                
                # FINAL CLEANUP: Strip all dashes
                final_feedback = response.text.replace("-", "").replace("—", "")
                
                st.write(final_feedback)
                st.code(final_feedback, language="markdown")
