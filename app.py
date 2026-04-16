import streamlit as st
from google import genai
import re
from datetime import datetime

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Shredlane Prime", layout="wide", page_icon="⚡")
st.title("⚡ Shredlane Prime: Automation Hub")

api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()
client = None
active_model = "gemini-3-flash-preview"

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        st.sidebar.success("✅ Doctrine Online")
    except Exception as e:
        st.sidebar.error(f"⚠️ Connection Failed: {e}")

mode = st.sidebar.radio("Navigation", ["Meal Builder", "Audit Engine"])

# --- 2. THE REFINED SHREDLANE DOCTRINE ---
SHREDLANE_DOCTRINE = """
SHREDLANE DOCTRINE RULES:
1. TARGETS: Use the client's specific Calorie and Protein targets.
2. MEAL STRUCTURE: Always provide Option 1 (Two Small Meals) and Option 2 (One Big Meal).
3. EGG RULE: Track eggs by NUMBER (e.g., 3 Eggs). All other items (Meat, Soy, Carbs) in GRAMS (g).
4. WEIGHING: 
   • Weigh RAW: Meat, Fish, Rice, Potatoes, Soy Chunks, Omena, Veggies.
   • Weigh COOKED: Ugali, Beans, Lentils.
5. THE OIL TAX: If any meal is 'Restaurant Style', add a +15g Vegetable Oil log line.
6. THE CHAI SPLIT: Log Milk (ml) and Sugar (g) separately. No 'Cup of Tea' entries.
7. SATIETY WARNING: If target is <= 1300kcal and no greens are listed, add: "⚠️ WARNING: High calorie density. Add 150g greens to prevent hunger."
8. FORMATTING: Use Bullet Points (•) ONLY. Never use dashes (-). Use Bold headers for sections.
"""

# --- 3. MEAL BUILDER ---
if mode == "Meal Builder":
    st.header("🛠 Your Custom Meal Builder")
    col1, col2 = st.columns(2)
    with col1:
        target_cal = st.text_input("Daily Calorie Target (e.g., 1200-1300)")
        target_pro = st.text_input("Daily Protein Target (e.g., 80-100g)")
    with col2:
        ingredients = st.text_area("Ingredients available:")

    if st.button("🏗️ Build My Shredlane Meals"):
        if not target_cal or not ingredients:
            st.error("Please enter targets and ingredients.")
        else:
            with st.spinner("Building meals..."):
                try:
                    builder_prompt = f"""
                    {SHREDLANE_DOCTRINE}
                    
                    TASK: Create a meal plan for: {target_cal} kcal and {target_pro} protein using {ingredients}.
                    
                    MANDATORY STRUCTURE:
                    • **TARGET:** [Total kcal] | [Total Protein]
                    • **⚠️ WARNING:** [Include Satiety Warning if target <= 1300kcal]
                    
                    **OPTION 1: TWO SMALL MEALS**
                    • **Meal 1:** [List ingredients + exact weights/numbers]
                    • **Meal 2:** [List ingredients + exact weights/numbers]
                    
                    **OPTION 2: ONE BIG MEAL**
                    • **The Feast:** [List all ingredients for the full day + exact weights/numbers]
                    
                    **MyNetDiary LOG LINES:**
                    • [Item 1]: [Grams/Numbers]
                    • [Item 2]: [Grams/Numbers]
                    """
                    res = client.models.generate_content(model=active_model, contents=builder_prompt)
                    st.markdown(res.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Builder Error: {e}")

# --- 4. AUDIT ENGINE ---
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
                try:
                    audit_prompt = f"""
                    {SHREDLANE_DOCTRINE}
                    TASK: Audit this {gender} client's log.
                    TARGETS: {client_target}
                    DATA: {check_in_data}
                    
                    MANDATORY STRUCTURE:
                    • **STATUS:** [🟢 PASSED / 🔴 OVER BUDGET / 🟡 UNDER PROTEIN]
                    • **CALORIES:** [Total logged] / [Target]
                    • **PROTEIN:** [Total logged] / [Target]
                    • **DOCTRINE VIOLATIONS:** [List any violations like egg weight, hidden oils, or 'handfuls']
                    • **COACH ADVICE:** [1-2 sentences of firm advice]
                    """
                    response = client.models.generate_content(model=active_model, contents=audit_prompt)
                    st.markdown(response.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Audit Error: {e}")
