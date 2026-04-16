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

# Sidebar Navigation - Both engines are here
mode = st.sidebar.radio("Navigation", ["Meal Builder", "Audit Engine"])

# --- 2. THE STRENGTHENED DOCTRINE ---
SHREDLANE_DOCTRINE = """
SHREDLANE DOCTRINE RULES:
1. TARGETS: Use the client's specific Calorie and Protein targets.
2. MEAL STRUCTURE: Always provide Option 1 (Two Small Meals) and Option 2 (One Big Meal).
3. EGG RULE: Eggs are tracked by NUMBER (e.g., 2 Eggs). All other proteins are in GRAMS (g).
4. WEIGHING: 
   • Weigh RAW: Meat, Fish, Rice, Potatoes, Soy Chunks, Omena, Veggies.
   • Weigh COOKED: Ugali, Beans, Lentils.
5. THE OIL TAX: If any meal is 'Restaurant Style', add a +15g Vegetable Oil log line.
6. THE CHAI SPLIT: Log Milk (ml) and Sugar (g) separately. No 'Cup of Tea' entries.
7. SATIETY WARNING: If target is <= 1300kcal and no greens are listed, add: "⚠️ WARNING: High calorie density. Add 150g greens to prevent hunger."
8. AUDIT PENALTY: If a high-calorie food (Nuts, Avocado, Ghee) is logged without grams, use the highest-calorie entry available.
9. CHICKEN RULE: Reject 'Chicken'. Must specify cut (Breast/Thigh) and bone-free.
10. FORMATTING: Use Bullet Points (•) ONLY. Never use dashes (-).
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
            with st.spinner("Enforcing Doctrine..."):
                try:
                    builder_prompt = f"""
                    {SHREDLANE_DOCTRINE}
                    TASK: Create a meal plan using: {ingredients}.
                    TARGET: {target_cal} kcal and {target_pro} protein.
                    
                    MANDATORY STRUCTURE:
                    - Option 1 (Two Small Meals): List exact grams/numbers for Meal 1 and Meal 2.
                    - Option 2 (One Big Meal): List exact grams/numbers for the full day.
                    - MyNetDiary LOG: Exact lines for the app.
                    """
                    res = client.models.generate_content(model=active_model, contents=builder_prompt)
                    st.markdown(res.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Builder Error: {e}")

# --- 4. AUDIT ENGINE (RESTORED) ---
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
            with st.spinner("Analyzing against Doctrine..."):
                try:
                    audit_prompt = f"""
                    {SHREDLANE_DOCTRINE}
                    TASK: Audit this {gender} client's log.
                    TARGETS: {client_target}
                    DATA: {check_in_data}
                    
                    AUDIT PROTOCOL:
                    1. Check if they weighed everything (no 'handfuls' or 'bowls').
                    2. Check if they hit the protein floor for their target.
                    3. Flag 'Chicken' if the cut isn't specified.
                    4. Check for hidden oils or un-split Chai.
                    5. TONE: Firm, Grade 7 English. Use Bullet Points (•).
                    """
                    response = client.models.generate_content(model=active_model, contents=audit_prompt)
                    st.markdown(response.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Audit Error: {e}")
