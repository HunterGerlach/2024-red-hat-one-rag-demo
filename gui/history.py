import streamlit as st

from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage
from streamlit_chat import message

class ChatHistory:
    def __init__(self, history_key="chat_history"):
        self.history_key = history_key
        if history_key not in st.session_state:
            st.session_state[history_key] = ConversationBufferMemory(memory_key=history_key, return_messages=True)
        self.history = st.session_state[history_key]

    def reset(self):
        st.session_state[self.history_key].clear()
        st.session_state["reset_chat"] = False

    def default_greeting(self):
        return "Hi ! 👋"

    def default_prompt(self, topic):
        return f"Hello ! Ask me anything about {topic} 🤗"

    def initialize(self, topic):
        message(self.default_greeting(), key='hi', avatar_style="adventurer", is_user=True)
        message(self.default_prompt(topic), key='ai', avatar_style="thumbs")

    def generate_messages(self, container, history_key="chat_history"):
            chat_history = st.session_state.get(history_key)
            if chat_history:
                with container:
                    messages = chat_history.chat_memory.messages
                    for i, msg in enumerate(messages):
                        if isinstance(msg, HumanMessage):
                            message(msg.content, is_user=True, key=f"{i}_user_{history_key}", avatar_style="adventurer")
                        elif isinstance(msg, AIMessage):
                            message(msg.content, key=f"{i}_{history_key}", avatar_style="thumbs")

    def get_full_conversation(self):
        """Retrieve the full conversation history as a list of messages."""
        return [str(message) for message in self.history.chat_memory.messages]
