import streamlit as st
from google import genai
import re
from datetime import datetime

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Shredlane Prime", layout="wide", page_icon="⚡")
st.title("⚡ Shredlane Prime: Meal Builder")

# Accessing Secrets
api_key = st.secrets.get("GOOGLE_API_KEY", "").strip()

# Initialize Client
client = None
active_model = "gemini-3-flash-preview" # 2026 Stable Standard

if api_key:
    try:
        client = genai.Client(api_key=api_key)
        st.sidebar.success("✅ Doctrine Online")
    except Exception as e:
        st.sidebar.error(f"⚠️ Connection Failed: {e}")

# Navigation
mode = st.sidebar.radio("Navigation", ["Meal Builder", "Audit Engine"])

# --- 2. THE SHREDLANE DOCTRINE (RE-CREATED) ---
SHREDLANE_DOCTRINE = """
SHREDLANE DOCTRINE RULES:
1. TARGETS: The client provides their own Calorie and Protein targets.
2. MEAL STRUCTURE: Always provide two distinct options:
   • OPTION 1: Two Small Meals (split the daily targets in half).
   • OPTION 2: One Big Meal (use the full daily target for one massive meal).
3. EGG RULE: Eggs are tracked by NUMBER (e.g., 2 Eggs, 3 Eggs). All other proteins are in GRAMS (g).
4. WEIGHING:
   • Weigh RAW: Meat, Fish, Rice, Potatoes, Soy Chunks, Omena, Veggies.
   • Weigh COOKED: Ugali, Beans, Lentils.
5. THE OIL TAX: If any meal is 'Restaurant Style', add a +15g Vegetable Oil log line.
6. THE CHAI SPLIT: Log Milk (ml) and Sugar (g) separately. No 'Cup of Tea' entries.
7. SATIETY WARNING: If target is <= 1300kcal and no greens are listed, add: "⚠️ WARNING: High calorie density. Add 150g greens to prevent hunger."
8. FORMATTING: Use Bullet Points (•) ONLY. Never use dashes (-). Use MyNetDiary log lines.
9. TONE: Firm, Professional, Grade 7 English.
"""

# --- 3. MEAL BUILDER ---
if mode == "Meal Builder":
    st.header("🛠 Your Custom Meal Builder")
    
    col1, col2 = st.columns(2)
    with col1:
        target_cal = st.text_input("Daily Calorie Target (e.g., 1200-1300)")
        target_pro = st.text_input("Daily Protein Target (e.g., 80-100g)")
    with col2:
        ingredients = st.text_area("What ingredients do you have today?", placeholder="e.g. Beef, Rice, Eggs, Spinach")

    if st.button("🏗️ Build My Shredlane Meals"):
        if not target_cal or not ingredients:
            st.error("Please enter your targets and ingredients.")
        else:
            with st.spinner("Calculating..."):
                try:
                    builder_prompt = f"""
                    {SHREDLANE_DOCTRINE}
                    
                    TASK: Build meals for a client with:
                    TARGET: {target_cal} kcal and {target_pro} protein.
                    INGREDIENTS: {ingredients}
                    
                    Structure the output exactly like this:
                    1. Option 1 (Two Small Meals): Show calories/protein per meal.
                    2. Option 2 (One Big Meal): Show full calorie/protein count.
                    3. MyNetDiary LOG lines: Exact text to type into the app.
                    """
                    res = client.models.generate_content(model=active_model, contents=builder_prompt)
                    st.markdown(res.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Builder Error: {e}")

# --- 4. AUDIT ENGINE ---
elif mode == "Audit Engine":
    st.header("📋 Check-in Audit")
    
    col1, col2 = st.columns(2)
    with col1:
        client_target = st.text_input("Current Targets")
        gender = st.selectbox("Gender", ["Female", "Male"])
    
    check_in_data = st.text_area("Paste your WhatsApp/MyNetDiary logs here:", height=200)
    
    if st.button("🚀 Run Audit"):
        with st.spinner("Analyzing..."):
            try:
                audit_prompt = f"""
                {SHREDLANE_DOCTRINE}
                
                TASK: Audit this {gender} client's data.
                TARGETS: {client_target}
                DATA: {check_in_data}
                
                Check for: 'handfuls', unweighed meat, unspecific chicken, hidden oils, or missed protein floors.
                """
                response = client.models.generate_content(model=active_model, contents=audit_prompt)
                st.markdown(response.text.replace("- ", "• "))
            except Exception as e:
                st.error(f"Audit Error: {e}")
