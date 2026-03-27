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
    st.session_state.messages = [
        (
            "assistant",
            "👋 Welcome to your AI Movie Assistant!\n\n"
            "Here’s what you can do:\n\n"
            "🎥 Recommend movies:\n"
            "→ 'Recommend movies like Inception'\n\n"
            "🔍 Search movies:\n"
            "→ 'Search Batman'\n\n"
            "📌 Add to watchlist:\n"
            "→ 'Add Inception to watchlist for Rupesh'\n\n"
            "📋 View watchlist:\n"
            "→ 'Show watchlist for Rupesh'\n\n"
            "✅ Mark as watched:\n"
            "→ 'Mark Inception as watched for Rupesh'\n\n"
            "📝 Add your own movies:\n"
            "→ 'Add a new movie called XYZ'\n\n"
            "Just type naturally—I’ll handle the rest!",
        )
    ]

# =========================
# DISPLAY CHAT HISTORY
# =========================

for role, msg in st.session_state.messages:
    with st.chat_message(role):
        # 🎯 HANDLE SINGLE MOVIE DETAILS
        if isinstance(msg, dict) and "title" in msg:
            st.markdown(f"""
        ### 🎬 {msg["title"]}

        ⭐ **Rating:** {msg["rating"]} ({msg["votes"]} votes)

        🎭 **Genres:** {msg["genres"]}

        🔑 **Keywords:** {msg["keywords"]}

        👥 **Cast:** {msg["cast"]}

        🎬 **Director:** {msg["director"]}

        🧠 **Overview:**
        {msg["overview"]}
        """)

        # 🎯 HANDLE WATCHLIST (list of dict with expectation)
        elif (
            isinstance(msg, list)
            and len(msg) > 0
            and isinstance(msg[0], dict)
            and "expectation" in msg[0]
        ):
            for movie in msg:
                with st.expander(f"🎬 {movie['title']}"):
                    st.markdown(f"""
        ⭐ **Expectation:** {movie["expectation"]}

        ⏰ **Planned Time:** {movie["watch_time"]}
        """)

        # 🎯 HANDLE STRUCTURED RESPONSE/TOP Movies
        elif isinstance(msg, list) and len(msg) > 0 and isinstance(msg[0], dict):
            for movie in msg:
                with st.expander(
                    f"🎬 {movie['title']} (⭐ {movie.get('rating', 'N/A')})"
                ):
                    st.markdown(f"""
**Overview:**
{movie.get("overview", "No description available")}
""")

        # 🎯 HANDLE NORMAL LIST
        elif isinstance(msg, list):
            for r in msg:
                st.write(f"• {r}")

        # 🎯 HANDLE STRING
        else:
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

            # 🎯 HANDLE SINGLE MOVIE DETAILS
            if isinstance(response, dict) and "title" in response:
                st.markdown(f"""
            ### 🎬 {response["title"]}

            ⭐ **Rating:** {response["rating"]} ({response["votes"]} votes)

            🎭 **Genres:** {response["genres"]}

            🔑 **Keywords:** {response["keywords"]}

            👥 **Cast:** {response["cast"]}

            🎬 **Director:** {response["director"]}

            🧠 **Overview:**
            {response["overview"]}
            """)

            # 🎯 HANDLE WATCHLIST (list of dict with expectation)
            elif (
                isinstance(response, list)
                and len(response) > 0
                and isinstance(response[0], dict)
                and "expectation" in response[0]
            ):
                for movie in response:
                    with st.expander(f"🎬 {movie['title']}"):
                        st.markdown(f"""
                    ⭐ **Expectation:** {movie["expectation"]}

                    ⏰ **Planned Time:** {movie["watch_time"]}
                    """)

            # 🎯 HANDLE STRUCTURED LIST (top_movies verbose)
            elif (
                isinstance(response, list)
                and len(response) > 0
                and isinstance(response[0], dict)
            ):
                for movie in response:
                    with st.expander(
                        f"🎬 {movie['title']} (⭐ {movie.get('rating', 'N/A')})"
                    ):
                        st.markdown(f"""
            **Overview:**
            {movie.get("overview", "No description available")}
            """)

            # 🎯 HANDLE NORMAL LIST
            elif isinstance(response, list):
                for r in response:
                    st.write(f"• {r}")

            # 🎯 HANDLE STRING
            else:
                st.write(response)

    # Store assistant response
    st.session_state.messages.append(("assistant", response))
