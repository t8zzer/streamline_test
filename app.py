import openai
import streamlit as st
from dotenv import load_dotenv
import os
import shelve

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

st.title("ChatGPT-like Chatbot Demo")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"

# Ensure openai_model is initialized in session state
if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-3.5-turbo"


# Load chat history from shelve file
def load_chat_history():
    try:
        with shelve.open("chat_history") as db:
            return db.get("messages", [])
    except Exception:
        return []


# Save chat history to shelve file
def save_chat_history(messages):
    try:
        with shelve.open("chat_history") as db:
            db["messages"] = messages
    except Exception:
        pass


# Initialize or load chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = load_chat_history()

# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state["messages"] = []
        save_chat_history([])

# Display chat messages
for message in st.session_state["messages"]:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Main chat interface
if prompt := st.chat_input("How can I help?"):
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar=BOT_AVATAR):
        message_placeholder = st.empty()
        full_response = ""
        for response in openai.ChatCompletion.create(
            model=st.session_state["openai_model"],
            messages=st.session_state["messages"],
            stream=True,
        ):
            full_response += response.choices[0].delta.content or ""
            message_placeholder.markdown(full_response + "|")
        message_placeholder.markdown(full_response)
    st.session_state["messages"].append({"role": "assistant", "content": full_response})

# Save chat history after each interaction
save_chat_history(st.session_state["messages"])
