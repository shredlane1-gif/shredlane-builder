import streamlit as st
from google import genai
import re
from datetime import datetime

# --- SETUP ---
st.set_page_config(page_title="Shredlane Prime", layout="wide", page_icon="⚡")
st.title("⚡ Shredlane Prime: Meal Builder")

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

# --- THE STRENGTHENED DOCTRINE ---
SHREDLANE_DOCTRINE = """
SHREDLANE DOCTRINE RULES:
1. TARGETS: Use the client's specific Calorie and Protein targets.
2. MEAL STRUCTURE: You MUST provide exact ingredient weights for every meal.
3. EGG RULE: Eggs are tracked by NUMBER (e.g., 2 Eggs). All other proteins are in GRAMS (g).
4. WEIGHING: 
   • Weigh RAW: Meat, Fish, Rice, Potatoes, Soy Chunks, Omena, Veggies.
   • Weigh COOKED: Ugali, Beans, Lentils.
5. THE OIL TAX: If any meal is 'Restaurant Style', add a +15g Vegetable Oil log line.
6. SATIETY WARNING: If target is <= 1300kcal and no greens are listed, add: "⚠️ WARNING: High calorie density. Add 150g greens to prevent hunger."
7. FORMATTING: Use Bullet Points (•) ONLY. Never use dashes (-).

MANDATORY OUTPUT STRUCTURE (DO NOT DEVIATE):
• OPTION 1: TWO SMALL MEALS
  - Meal 1: [List every ingredient with grams/numbers]
  - Meal 2: [List every ingredient with grams/numbers]
  - MyNetDiary LOG: [Exact text for the whole day]

• OPTION 2: ONE BIG MEAL
  - The Feast: [List every ingredient with grams/numbers]
  - MyNetDiary LOG: [Exact text for the whole day]
"""

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
                    # WE FORCE THE STRUCTURE HERE
                    builder_prompt = f"""
                    {SHREDLANE_DOCTRINE}
                    
                    TASK: Create a meal plan using: {ingredients}.
                    TARGET: {target_cal} kcal and {target_pro} protein.
                    
                    CRITICAL: You must specify the exact GRAMS of each ingredient for each meal. 
                    Do not just list the total at the end.
                    """
                    res = client.models.generate_content(model=active_model, contents=builder_prompt)
                    st.markdown(res.text.replace("- ", "• "))
                except Exception as e:
                    st.error(f"Builder Error: {e}")

# (Audit Engine code remains same as previous)
