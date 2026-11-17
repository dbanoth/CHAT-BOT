import os

import streamlit as st
from groq import Groq
from supabase import Client, create_client

# Page config
st.set_page_config(page_title="AI Chatbot", page_icon="⚡", layout="wide")
st.markdown("<style>.stApp{max-width:1100px;margin:0 auto;}</style>", unsafe_allow_html=True)


def get_secret(name):
    try:
        return st.secrets[name]
    except Exception:
        return os.getenv(name)


# Keys come from Streamlit secrets or environment variables, never from source code
GROQ_API_KEY = get_secret("GROQ_API_KEY")
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_KEY = get_secret("SUPABASE_KEY")

if not GROQ_API_KEY:
    st.error("Groq API key not found.")
    st.stop()

try:
    groq_client = Groq(api_key=GROQ_API_KEY)
except Exception as e:
    st.error(f"Failed to initialize Groq: {e}")
    st.stop()

supabase = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
else:
    st.warning("Supabase is not configured. Chat history will not be saved.")

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.title("⚡ AI Chatbot")
    user_name = st.text_input("Your Name", value="Anonymous")
    model = st.selectbox("Model", ["llama-3.1-8b-instant"])
    temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
    max_tokens = st.slider("Max tokens", 100, 2000, 512, 50)
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()

st.title("💬 Chat with Groq")

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                # Send the last 10 messages as context
                api_messages = [{"role": "system", "content": "You are a helpful assistant."}]
                for m in st.session_state.messages[-10:]:
                    api_messages.append({"role": m["role"], "content": m["content"]})

                resp = groq_client.chat.completions.create(
                    messages=api_messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    top_p=1,
                    stream=False,
                )
                assistant_response = resp.choices[0].message.content
                st.write(assistant_response)
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                if supabase:
                    try:
                        supabase.table("chat_history").insert({
                            "user_name": user_name,
                            "message": prompt,
                            "response": assistant_response,
                        }).execute()
                        st.success("Saved to database", icon="✅")
                    except Exception as e:
                        st.error(f"Failed to save: {e}")

            except Exception as e:
                st.error(f"Groq request failed: {e}")
