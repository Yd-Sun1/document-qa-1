import streamlit as st
from openai import OpenAI

st.title("Lab 3 - Streaming Chatbot")

client = OpenAI(api_key=st.secrets["openai_api_key"])

def get_buffer(messages):
    system_messages = [
        message for message in messages
        if message["role"] == "system"
    ]

    conversation_messages = [
        message for message in messages
        if message["role"] != "system"
    ]

    buffer = []
    user_count = 0

    for message in reversed(conversation_messages):
        buffer.insert(0, message)

        if message["role"] == "user":
            user_count += 1

        if user_count == 2:
            break

    return system_messages + buffer

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """
            You are a helpful chatbot.
            Answer questions using simple language that a 10-year-old can understand.
            After answering a question, ask: "Do you want more info?"
            If the user says yes, provide more information and ask again: "Do you want more info?"
            If the user says no, ask: "What can I help you with?"
            """
        }
    ]

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
if prompt := st.chat_input("Ask me a question"):

    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

        buffer_messages = get_buffer(st.session_state.messages)

        stream = client.chat.completions.create(
        model="gpt-5-nano",
        messages=st.session_state.messages,
        stream=True
    )

    with st.chat_message("assistant"):
        response = st.write_stream(stream)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )