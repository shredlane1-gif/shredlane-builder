import streamlit as st
import google.generativeai as genai

st.title("💪 Shredlane Prime Meal Builder")

api_key = st.secrets.get("GOOGLE_API_KEY")

if not api_key:
    st.error("API Key not found in Secrets. Please add GOOGLE_API_KEY to your Streamlit settings.")
else:
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3-flash-preview")

        # Added Gender selection for accurate calorie targeting
        gender = st.selectbox("Select Gender:", ["Female", "Male"])
        weight = st.text_input("Weight (kg):")
        ingredients = st.text_area("Ingredients:")

        if st.button("Build Plan"):
            if not weight or not ingredients:
                st.error("Please enter both your weight and your ingredients.")
            else:
                shredlane_logic = r"""
IDENTITY:
You are the SHREDLANE MEAL BUILDER.
Output quantities and MyNetDiary log lines only. Do not suggest recipes, dishes, or cooking instructions.

CALORIE & TIER RULES:
1. IF FEMALE: Total daily calories MUST NOT exceed 1,500 kcal, regardless of weight.
2. IF WEIGHT < 80kg: Total daily calories MUST be 1,200 kcal.
3. IF WEIGHT >= 80kg AND MALE: Total daily calories 1,800 kcal.

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
4. Round all weights to nearest 5g.
5. Provide specific MyNetDiary log lines for every item.
                """
                
                full_prompt = f"System: {shredlane_logic}\n\nClient Input: Gender: {gender}, Weight: {weight}kg, Ingredients: {ingredients}"
                
                with st.spinner("Building your meal plan..."):
                    response = model.generate_content(full_prompt)
                    st.write(response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")
