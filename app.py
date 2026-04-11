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

        gender = st.selectbox("Select Gender:", ["Female", "Male"])
        weight = st.text_input("Weight (kg):")
        ingredients = st.text_area("Ingredients (List everything available):")

        if st.button("Build Plan"):
            if not weight or not ingredients:
                st.error("Please enter both your weight and your ingredients.")
            else:
                shredlane_logic = r"""
IDENTITY:
You are the SHREDLANE MEAL BUILDER.
You are strictly forbidden from adding ingredients NOT in the provided list.

CALORIE & MACRO TARGETS:
- IF FEMALE: Total daily target 1,500 kcal.
- IF WEIGHT < 80kg: Total daily target 1,200 kcal.
- IF WEIGHT >= 80kg AND MALE: Total daily target 1,800 kcal.
- FAT CONSTRAINT: Total daily fat calories MUST be between 20% and 30% of total calories.

REQUIRED OUTPUT STRUCTURE:

OPTION 1: TWO MEALS (Daily target split 50/50)
- MEAL 1: List ingredients/grams. Provide MyNetDiary log line per ingredient.
- MEAL 2: List ingredients/grams. Provide MyNetDiary log line per ingredient.

OPTION 2: BIG MEAL (Batch Cook)
- This is ONE recipe containing 100% of the daily calories and protein.
- Provide TOTAL batch weights.
- Provide the log line "per serving" (divide by 2).

FORMATTING RULES:
- Weights in GRAMS only. 
- Use the provided ingredient list ONLY.
- Log lines: Name - Weight - MyNetDiary Term.
- Round all weights to nearest 5g.
- No recipes, no dishes, no extra advice. Output plans only.
                """
                
                full_prompt = f"System: {shredlane_logic}\n\nClient Input: Gender: {gender}, Weight: {weight}kg, Ingredients: {ingredients}"
                
                with st.spinner("Building your meal plan..."):
                    response = model.generate_content(full_prompt)
                    st.write(response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")
