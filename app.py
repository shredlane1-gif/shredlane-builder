import streamlit as st
from google import genai
import re
from datetime import datetime

# --- 1. SETUP ---
st.set_page_config(page_title="Shredlane Prime", layout="wide", page_icon="⚡")
st.title("⚡ Shredlane Prime: Automation Hub")

api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
client = None

# Fallback Model List (2026 Stable Models)
MODEL_PRIORITY = ["gemini-3-flash-preview", "gemini-2.5-flash", "gemini-1.5-flash"]

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        st.sidebar.success("✅ Doctrine Online")
    except Exception as e:
        st.sidebar.error(f"⚠️ Connection Failed: {e}")

mode = st.sidebar.radio("Navigation", ["Meal Builder", "Audit Engine"])

# --- 2. THE DOCTRINE ---
SHREDLANE_DOCTRINE = """
SHREDLANE DOCTRINE RULES:
1. TARGETS: Use the client's specific Calorie and Protein targets.
2. MEAL STRUCTURE: Always provide Option 1 (Two Small Meals) and Option 2 (One Big Meal).
3. EGG RULE: Track eggs by NUMBER (e.g., 3 Eggs). All other items in GRAMS (g).
4. WEIGHING: Weigh RAW (Meat, Rice, Soy, Omena). Weigh COOKED (Ugali, Beans, Lentils).
5. THE OIL TAX: If 'Restaurant Style', add +15g Vegetable Oil log line.
6. THE CHAI SPLIT: Log Milk (ml) and Sugar (g) separately.
7. SATIETY WARNING: If target <= 1300kcal and no greens, add: "⚠️ WARNING: High calorie density. Add 150g greens."
8. FORMATTING: Use Bullet Points (•) ONLY. Use Bold headers.
"""

# --- 3. THE SMART RUNNER (Handles 503 Errors) ---
def run_shredlane_task(prompt):
    for model_id in MODEL_PRIORITY:
        try:
            res = client.models.generate_content(model=model_id, contents=prompt)
            return res.text
        except Exception as e:
            if "503" in str(e) or "429" in str(e):
                continue # Try the next model in the list
            else:
                return f"Error: {e}"
    return "All models are currently busy. Please wait 60 seconds and try again."

# --- 4. MEAL BUILDER ---
if mode == "Meal Builder":
    st.header("🛠 Your Custom Meal Builder")
    col1, col2 = st.columns(2)
    with col1:
        target_cal = st.text_input("Daily Calorie Target")
        target_pro = st.text_input("Daily Protein Target")
    with col2:
        ingredients = st.text_area("Ingredients available:")

    if st.button("🏗️ Build My Shredlane Meals"):
        if not target_cal or not ingredients:
            st.error("Please enter targets and ingredients.")
        else:
            with st.spinner("Finding an available AI brain..."):
                builder_prompt = f"""
                {SHREDLANE_DOCTRINE}
                TASK: Build meals for {target_cal} kcal and {target_pro} protein using {ingredients}.
                STRUCTURE:
                • **TARGET:** [Target kcal] | [Protein]
                • **⚠️ WARNING:** [If target <= 1300kcal]
                **OPTION 1: TWO SMALL MEALS**
                • **Meal 1:** [Ingredients + weights]
                • **Meal 2:** [Ingredients + weights]
                **OPTION 2: ONE BIG MEAL**
                • **The Feast:** [All ingredients + weights]
                **MyNetDiary LOG LINES:**
                • [Item]: [Grams/Numbers]
                """
                output = run_shredlane_task(builder_prompt)
                st.markdown(output.replace("- ", "• "))

# --- 5. AUDIT ENGINE ---
elif mode == "Audit Engine":
    st.header("📋 Client Check-in Audit")
    col1, col2 = st.columns(2)
    with col1:
        client_target = st.text_input("Client's Daily Targets")
        gender = st.selectbox("Gender", ["Female", "Male"])
    
    check_in_data = st.text_area("Paste WhatsApp/MyNetDiary logs here:", height=250)
    
    if st.button("🚀 Run Audit"):
        if not check_in_data:
            st.error("Paste data to audit.")
        else:
            with st.spinner("Analyzing..."):
                audit_prompt = f"""
                {SHREDLANE_DOCTRINE}
                TASK: Audit this {gender} client log for targets: {client_target}.
                DATA: {check_in_data}
                STRUCTURE:
                • **STATUS:** [🟢 PASSED / 🔴 OVER BUDGET / 🟡 UNDER PROTEIN]
                • **CALORIES:** [Logged] / [Target]
                • **PROTEIN:** [Logged] / [Target]
                • **DOCTRINE VIOLATIONS:** [List violations]
                • **COACH ADVICE:** [Firm advice]
                """
                output = run_shredlane_task(audit_prompt)
                st.markdown(output.replace("- ", "• "))
