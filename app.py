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
            st.warning("Password required.")
            st.stop()

        with st.form("audit_form"):
            client_name = st.text_input("Client Name")
            targets = st.text_input("Daily Targets (e.g., 1200 kcal / 90g Pro)")
            whatsapp_data = st.text_area("WhatsApp Check-in (Steps, Weight, Sleep, Water)")
            diary_log = st.text_area("MyNetDiary Log")
            submit_audit = st.form_submit_button("Generate Feedback")

        if submit_audit:
            # THIS IS THE FINAL CLEAN PROMPT
            doctrine_prompt = f"""
            You are the Shredlane Coach. Your job is to give daily feedback to a client.
            
            FOLLOW THESE RULES:
            1. Write in very simple, easy-to-understand English (Grade 7 level).
            2. Do NOT use dashes (-) or (—) anywhere in your output. Use numbers or plain text.
            3. Write only ONE response. Do not repeat yourself.
            4. Structure the message exactly like this:
               
               STATUS: (Use ✅ for Good, ⚠️ for Warning, ❌ for Bad)
               
               NUMBERS:
               Calories: [X] kcal
               Protein: [X]g
               Steps: [X]
               Sleep: [X]
               
               YOUR PROGRESS:
               [Briefly mention weight and waist trend]
               
               TOMORROW'S PLAN:
               1. [Instruction 1]
               2. [Instruction 2]
               3. [Instruction 3]
               
               COACH'S NOTE:
               [Write 2 to 3 simple sentences about their performance. Be kind but tell them how to improve.]

            THE RULES:
            - Always tell them to weigh food before cooking.
            - Always be specific about food (e.g., say 'chicken breast' not just 'chicken').
            - If steps are low, tell them to walk more.

            INPUTS:
            Client: {client_name}
            Targets: {targets}
            WhatsApp Data: {whatsapp_data}
            MyNetDiary Log: {diary_log}
            """
            
            with st.spinner("Analyzing data..."):
                response = model.generate_content(doctrine_prompt)
                # Final cleanup
                final_feedback = response.text.replace("-", "").replace("—", "")
                st.write(final_feedback)
                st.code(final_feedback, language="markdown")
