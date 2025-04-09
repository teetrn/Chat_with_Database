import streamlit as st
import pandas as pd
import google.generativeai as genai

# ===============================
# SETUP API KEY (Hardcoded)
# ===============================
DEFAULT_GEMINI_API_KEY = "AIzaSyAolFMOcNhhrKMnuLTPGGO7eS8UOxpmgfQ"

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
# Page Config & Styling
# ===============================
st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    /* Sidebar background color */
    [data-testid="stSidebar"] {
        background-color: #1e3a8a !important;
    }

    /* Sidebar text styling */
    [data-testid="stSidebar"] * {
        color: white !important;
        font-size: 1rem !important;
    }

    /* Optional: control sidebar padding */
    [data-testid="stSidebar"] > div:first-child {
        padding: 1rem;
    }

    /* Chat message styling */
    .chat-message {
        padding: 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .chat-user {
        background-color: #f3f4f6;
    }
    .chat-bot {
        background-color: #e5e7eb;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# Sidebar – File Uploads
# ===============================
with st.sidebar:
    st.markdown("### 📂 1. Upload CSV File")
    uploaded_file = st.file_uploader("Choose CSV", type=["csv"])
    if uploaded_file is not None:
        try:
            st.session_state.uploaded_data = pd.read_csv(uploaded_file)
            st.success("✅ CSV uploaded")
            st.dataframe(st.session_state.uploaded_data.head())
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    else:
        st.markdown("❗ ยังไม่ได้อัปโหลด CSV")

    st.markdown("---")

    st.markdown("### 📘 2. Data Dictionary (Optional)")
    data_dict_file = st.file_uploader("Choose Data Dictionary", type=["csv", "xlsx"])
    if data_dict_file is not None:
        try:
            if data_dict_file.name.endswith(".xlsx"):
                st.session_state.data_dictionary = pd.read_excel(data_dict_file)
            else:
                st.session_state.data_dictionary = pd.read_csv(data_dict_file)
            st.success("✅ Data Dictionary uploaded")
            st.dataframe(st.session_state.data_dictionary.head())
        except Exception as e:
            st.error(f"Error reading dictionary: {e}")
    else:
        st.markdown("ℹ️ ยังไม่อัปโหลด (ไม่บังคับ)")

    st.markdown("---")

    analyze_data_checkbox = st.checkbox("🔎 Enable AI Analysis", value=True)

# ===============================
# Chat Area
# ===============================
st.title("Chat with Your Data")

for role, message in st.session_state.chat_history:
    css_class = "chat-user" if role == "user" else "chat-bot"
    st.markdown(f"<div class='chat-message {css_class}'>{message}</div>", unsafe_allow_html=True)

if user_input := st.chat_input("Type your question here..."):
    st.session_state.chat_history.append(("user", user_input))
    st.markdown(f"<div class='chat-message chat-user'>{user_input}</div>", unsafe_allow_html=True)

    try:
        if st.session_state.uploaded_data is not None and analyze_data_checkbox:
            if "analyze" in user_input.lower() or "insight" in user_input.lower():
                data_description = st.session_state.uploaded_data.describe().to_string()

                if st.session_state.data_dictionary is not None:
                    data_dict_info = st.session_state.data_dictionary.to_string()
                    prompt = f"Analyze this dataset:\n\nData:\n{data_description}\n\nData Dictionary:\n{data_dict_info}"
                else:
                    prompt = f"Analyze this dataset:\n\n{data_description}"

                response = model.generate_content(prompt)
                bot_response = response.text
            else:
                response = model.generate_content(user_input)
                bot_response = response.text
        elif not analyze_data_checkbox:
            bot_response = "🔒 AI Analysis is disabled."
        else:
            bot_response = "📁 Please upload a CSV file first."

    except Exception as e:
        bot_response = f"❌ Error: {e}"

    st.session_state.chat_history.append(("assistant", bot_response))
    st.markdown(f"<div class='chat-message chat-bot'>{bot_response}</div>", unsafe_allow_html=True)
