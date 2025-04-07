import streamlit as st
import pandas as pd
import google.generativeai as genai

# Set up the Streamlit app layout
st.set_page_config(page_title="AI Chat with CSV", layout="wide")
st.title("My Chatbot and Data Analysis App")

# Sidebar – Controls and Uploads
with st.sidebar:
    st.header("🔧 Settings")

    # Capture Gemini API Key
    gemini_api_key = st.text_input("Gemini API Key", placeholder="Enter your API key...", type="password")

    # Initialize the Gemini Model
    model = None
    if gemini_api_key:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel("gemini-pro")
            st.success("✅ Gemini API Key configured")
        except Exception as e:
            st.error(f"Error setting up Gemini model: {e}")

    # Upload CSV File
    st.subheader("📁 Upload CSV for Analysis")
    uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            st.session_state.uploaded_data = pd.read_csv(uploaded_file)
            st.success("CSV uploaded successfully")
            st.write("📊 Preview")
            st.dataframe(st.session_state.uploaded_data.head())
        except Exception as e:
            st.error(f"Error reading the CSV file: {e}")

    # Checkbox for analysis toggle
    analyze_data_checkbox = st.checkbox("🔍 Analyze CSV Data with AI")

# Initialize session state if not already
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None

# Main area – Chat Interface
st.subheader("💬 Chat with AI")

# Display chat history
for role, message in st.session_state.chat_history:
    st.chat_message(role).markdown(message)

# Chat input
if user_input := st.chat_input("Type your message here..."):
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").markdown(user_input)

    if model:
        try:
            # AI Analysis
            if st.session_state.uploaded_data is not None and analyze_data_checkbox:
                if "analyze" in user_input.lower() or "insight" in user_input.lower():
                    data_description = st.session_state.uploaded_data.describe().to_string()
                    prompt = f"Analyze the following dataset and provide insights:\n\n{data_description}"
                    response = model.generate_content(prompt)
                    bot_response = response.text
                else:
                    response = model.generate_content(user_input)
                    bot_response = response.text
            elif not analyze_data_checkbox:
                bot_response = "❌ Data analysis is disabled. Please check the box in the sidebar."
            else:
                bot_response = "⚠️ Please upload a CSV file first."

            st.session_state.chat_history.append(("assistant", bot_response))
            st.chat_message("assistant").markdown(bot_response)
        except Exception as e:
            st.error(f"Error generating response: {e}")
    else:
        st.warning("⚠️ Please enter your Gemini API Key in the sidebar.")
