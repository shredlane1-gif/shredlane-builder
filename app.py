import streamlit as st
from google import genai
from datetime import datetime

st.set_page_config(page_title="Shredlane Prime", page_icon="⚡")
st.title("⚡ Shredlane Prime Automation")

# Connect to the New Engine
api_key = st.secrets.get("GOOGLE_API_KEY")
client = genai.Client(api_key=api_key)

# STABLE MODEL CHOICE
# We use 1.5-Flash because it is reliable for the Free Tier
active_model = "models/gemini-1.5-flash"

# Sidebar Navigation
mode = st.sidebar.selectbox("Choose Task", ["Client Audit", "Meal Builder"])

if mode == "Client Audit":
    name = st.text_input("Client Name (e.g., Merceline)")
    gender = st.selectbox("Gender", ["Female", "Male"])
    log = st.text_area("Paste MyNetDiary/WhatsApp Data")
    
    if st.button("Run Audit"):
        with st.spinner("Analyzing Shredlane Doctrine..."):
            prompt = f"Audit this {gender} client ({name}): {log}. Use • bullets. Firm tone. Grade 7 English."
            response = client.models.generate_content(model=active_model, contents=prompt)
            st.markdown(response.text.replace("- ", "• "))

elif mode == "Meal Builder":
    weight = st.text_input("Weight (kg)")
    ingredients = st.text_area("What ingredients do they have?")
    
    if st.button("Build Plan"):
        prompt = f"Build a meal plan for a {weight}kg person using {ingredients}. 2 options. • bullets."
        response = client.models.generate_content(model=active_model, contents=prompt)
        st.markdown(response.text.replace("- ", "• "))
