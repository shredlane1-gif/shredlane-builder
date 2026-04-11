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
Your ONLY job is to organize the ingredients provided by the client into a meal plan.

STRICT RULES:
1. USE ONLY PROVIDED INGREDIENTS. Do not suggest whey, protein powder, or anything not in the input list.
2. If the user input is incomplete, do not hallucinate items. Work only with what is provided.
3. Output MUST be strictly formatted into three sections: MEAL 1, MEAL 2, and BIG MEAL.
4. Each section MUST list the ingredient, the weight in grams, and the MyNetDiary log line.

CALORIE TARGETS:
- IF FEMALE: Max 1,500 kcal/day.
- IF WEIGHT < 80kg: Target 1,200 kcal/day.
- IF WEIGHT >= 80kg AND MALE: Target 1,800 kcal/day.

FORMAT:
MEAL 1
- [Ingredient]: [X]g
- MyNetDiary Log: [Search Term] - [X]g

MEAL 2
- [Ingredient]: [X]g
- MyNetDiary Log: [Search Term] - [X]g

BIG MEAL (Cook once, eat twice)
- [Ingredient]: [X]g total
- MyNetDiary Log: [Search Term] - [X]g per serving
                """
                
                full_prompt = f"System: {shredlane_logic}\n\nClient Input: Gender: {gender}, Weight: {weight}kg, Ingredients: {ingredients}"
                
                with st.spinner("Building your meal plan..."):
                    response = model.generate_content(full_prompt)
                    st.write(response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")
