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
    /* เปลี่ยนสีพื้นหลัง Sidebar แบบชัวร์ๆ */
    section[data-testid="stSidebar"] {
        background-color: #1e3a8a !important;
    }

    /* ทำให้ข้อความเป็นสีขาวและขนาดเล็ก */
    section[data-testid="stSidebar"] * {
        color: white !important;
        font-size: 0.85rem;
    }

    /* ย่อ Sidebar */
    section[data-testid="stSidebar"] {
        width: 250px !important;
    }

    /* ปรับ Main Content ตามความกว้างของ Sidebar */
    div[class^="block-container"] {
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# Layout Structure
# ===============================
col1, col2 = st.columns([0.7, 2.3])  # Sidebar / Chat area

# ===============================
# Sidebar – File Uploads
# ===============================
with col1:
    st.markdown("### <span class='sidebar-text'>📂 1. Upload CSV File</span>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("", type=["csv"], label_visibility="collapsed")
    if uploaded_file is not None:
        try:
            st.session_state.uploaded_data = pd.read_csv(uploaded_file)
            st.success("✅ CSV uploaded")
            st.dataframe(st.session_state.uploaded_data.head())
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    else:
        st.markdown("<span class='sidebar-text'>❗ ยังไม่ได้อัปโหลด CSV</span>", unsafe_allow_html=True)

    st.markdown("---")

    st.markdown("### <span class='sidebar-text'>📘 2. Data Dictionary (Optional)</span>", unsafe_allow_html=True)
    data_dict_file = st.file_uploader("", type=["csv", "xlsx"], label_visibility="collapsed")
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
        st.markdown("<span class='sidebar-text'>ℹ️ ยังไม่อัปโหลด (ไม่บังคับ)</span>", unsafe_allow_html=True)

    st.markdown("---")

    analyze_data_checkbox = st.checkbox("🔎 Enable AI Analysis", value=True)

# ===============================
# Chat Area
# ===============================
with col2:
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
