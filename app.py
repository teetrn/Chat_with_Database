import streamlit as st
import pandas as pd
import google.generativeai as genai

# ===============================
# SETUP API KEY (Hardcoded)
# ===============================
DEFAULT_GEMINI_API_KEY = "AAA123"

# Configure Gemini with the default API Key
try:
    genai.configure(api_key=DEFAULT_GEMINI_API_KEY)
    model = genai.GenerativeModel("gemini-pro")
except Exception as e:
    st.error(f"❌ Error setting up Gemini model: {e}")
    model = None

# ===============================
# Initialize Session State
# ===============================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "uploaded_data" not in st.session_state:
    st.session_state.uploaded_data = None
if "data_dictionary" not in st.session_state:
    st.session_state.data_dictionary = None

# ===============================
# Layout Setup
# ===============================
st.set_page_config(layout="wide")
col1, col2 = st.columns([1, 2])  # Sidebar / Chat area

# ===============================
# Sidebar – File Uploads
# ===============================
with col1:
    st.header("📂 Upload Zone")

    # Upload CSV file
    st.subheader("1️⃣ Upload CSV File")
    uploaded_file = st.file_uploader("Choose your CSV file", type=["csv"])
    if uploaded_file is not None:
        try:
            st.session_state.uploaded_data = pd.read_csv(uploaded_file)
            st.success("✅ CSV file uploaded successfully!")
            st.write("Preview of uploaded data:")
            st.dataframe(st.session_state.uploaded_data.head())
        except Exception as e:
            st.error(f"Error reading CSV: {e}")

    # Upload Data Dictionary (Optional)
    st.subheader("2️⃣ Upload Data Dictionary (Optional)")
    data_dict_file = st.file_uploader("Choose a Data Dictionary file", type=["csv", "xlsx"])
    if data_dict_file is not None:
        try:
            if data_dict_file.name.endswith(".xlsx"):
                st.session_state.data_dictionary = pd.read_excel(data_dict_file)
            else:
                st.session_state.data_dictionary = pd.read_csv(data_dict_file)
            st.success("✅ Data Dictionary uploaded successfully!")
            st.write("Preview of Data Dictionary:")
            st.dataframe(st.session_state.data_dictionary.head())
        except Exception as e:
            st.error(f"Error reading Data Dictionary: {e}")

    # Checkbox to enable analysis
    analyze_data_checkbox = st.checkbox("🔎 Enable AI Analysis", value=True)

# ===============================
# Main Chat Section
# ===============================
with col2:
    st.title("🤖 Chat with Your Data")
    for role, message in st.session_state.chat_history:
        st.chat_message(role).markdown(message)

    if user_input := st.chat_input("Type your question here..."):
        st.session_state.chat_history.append(("user", user_input))
        st.chat_message("user").markdown(user_input)

        try:
            if st.session_state.uploaded_data is not None and analyze_data_checkbox:
                # If user wants to analyze data
                if "analyze" in user_input.lower() or "insight" in user_input.lower():
                    data_description = st.session_state.uploaded_data.describe().to_string()

                    # Optional: include data dictionary in prompt
                    if st.session_state.data_dictionary is not None:
                        data_dict_info = st.session_state.data_dictionary.to_string()
                        prompt = f"Analyze the dataset below and provide insights:\n\nData:\n{data_description}\n\nData Dictionary:\n{data_dict_info}"
                    else:
                        prompt = f"Analyze the dataset below and provide insights:\n\n{data_description}"

                    response = model.generate_content(prompt)
                    bot_response = response.text
                else:
                    # General conversation
                    response = model.generate_content(user_input)
                    bot_response = response.text
            elif not analyze_data_checkbox:
                bot_response = "🔒 AI Analysis is disabled. Please enable the checkbox to analyze data."
            else:
                bot_response = "📁 Please upload a CSV file first."

        except Exception as e:
            bot_response = f"❌ Error: {e}"

        st.session_state.chat_history.append(("assistant", bot_response))
        st.chat_message("assistant").markdown(bot_response)
