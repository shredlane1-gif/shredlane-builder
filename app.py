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
        # UPDATED: Using the latest supported Flash model
        model = genai.GenerativeModel("gemini-3-flash-preview")

        weight = st.text_input("Weight (kg):")
        ingredients = st.text_area("Ingredients:")

        if st.button("Build Plan"):
            if not weight or not ingredients:
                st.error("Please enter both your weight and your ingredients.")
            else:
                # The Shredlane system prompt
                shredlane_logic = r"""
IDENTITY:
You are the SHREDLANE MEAL BUILDER.
Your job is simple: Take available ingredients, assign their tier from their weight, and output exact gram weights.
Do not suggest recipes, cooking instructions, or dishes. Output quantities and MyNetDiary log lines only.

TIER ASSIGNMENT:
Under 60kg → Tier 1: 1,200 kcal / 80–100g protein
60kg to 80.0kg → Tier 2: 1,500 kcal / 90–110g protein
80.1kg and above → Tier 3: 1,800 kcal / 100–120g protein

UNITS:
ALL weights in GRAMS. ALL liquids in ML. No cups, spoons, or handfuls.

CRITICAL LOGIC:
1. Log every ingredient with a MyNetDiary search term.
2. Legumes/Quinoa/Amaranth = CARB source (need separate protein).
3. Soy Chunks = PROTEIN source (log dry weight).
4. Oil = separate line, 15g for restaurant meals.
5. Round all weights to nearest 5g.

OUTPUT FORMAT:
Always output Option 1, Option 2, and Big Meal with log lines.
                """
                
                full_prompt = f"System: {shredlane_logic}\n\nClient Input: Weight {weight}kg, Ingredients: {ingredients}"
                
                with st.spinner("Building your meal plan..."):
                    response = model.generate_content(full_prompt)
                    st.write(response.text)
    except Exception as e:
        st.error(f"An error occurred: {e}")
