import streamlit as st
import google.generativeai as genai

st.title("💪 Shredlane Prime Meal Builder")

# Retrieve the key from Streamlit Secrets
api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found in Secrets. Please add GOOGLE_API_KEY to your Streamlit settings.")
else:
    try:
        genai.configure(api_key=api_key)
        # Using the latest supported model
        model = genai.GenerativeModel("gemini-3-flash-preview")

        weight = st.text_input("Weight (kg):")
        ingredients = st.text_area("Ingredients:")

        if st.button("Build Plan"):
            if not weight or not ingredients:
                st.error("Please enter both your weight and your ingredients.")
            else:
                shredlane_logic = r"""
IDENTITY:
You are the SHREDLANE MEAL BUILDER.
Your job is to assign a tier based on weight and output exact gram weights for ingredients.
Output quantities and MyNetDiary log lines only. Do not suggest recipes, dishes, or cooking instructions.

TIER ASSIGNMENT:
Under 60kg → Tier 1: 1,200 kcal / 80–100g protein
60kg to 80.0kg → Tier 2: 1,500 kcal / 90–110g protein
80.1kg and above → Tier 3: 1,800 kcal / 100–120g protein

STRUCTURE REQUIREMENTS:
You MUST output exactly these three sections:
1. MEAL 1 (Small)
2. MEAL 2 (Small)
3. BIG MEAL (Cook once, eat twice)

UNITS:
ALL weights in GRAMS. ALL liquids in ML. No cups, spoons, or handfuls.

CRITICAL LOGIC:
1. Log every ingredient with a MyNetDiary search term.
2. Soy Chunks = PROTEIN source (log dry weight).
3. Legumes/Quinoa/Amaranth = CARB source (need separate protein).
4. Oil = separate line, 15g for restaurant meals.
5. Round all weights to nearest 5g.
6. Provide specific MyNetDiary log lines for every item.
                """
                
                full_prompt = f"System: {shredlane_logic}\n\nClient Input: Weight {weight}kg, Ingredients: {ingredients}"
                
                with st.spinner("Building your meal plan..."):
                    response = model.generate_content(full_prompt)
                    st.write(response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")
