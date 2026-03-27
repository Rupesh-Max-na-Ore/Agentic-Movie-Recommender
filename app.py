import streamlit as st

from agent import run_agent

# =========================
# PAGE CONFIG
# =========================

st.set_page_config(
    page_title="Agentic Movie Assistant", page_icon="🎬", layout="centered"
)

st.title("🎬 Agentic Movie Assistant")
st.caption("AI-powered movie recommendations + watchlist manager")

# =========================
# SESSION STATE INIT
# =========================

if "messages" not in st.session_state:
    st.session_state.messages = []

# =========================
# DISPLAY CHAT HISTORY
# =========================

for role, msg in st.session_state.messages:
    with st.chat_message(role):
        st.write(msg)

# =========================
# USER INPUT
# =========================

user_input = st.chat_input("Ask about movies...")

if user_input:
    # Add user message
    st.session_state.messages.append(("user", user_input))

    with st.chat_message("user"):
        st.write(user_input)

    # Get agent response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(user_input)
            st.write(response)

    # Store assistant response
    st.session_state.messages.append(("assistant", response))
