import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import tempfile

from chat_management.chatbot import Chatbot
from embeddings.doc_embedding import DocEmbedding
from utils.utilities import Utilities


class Sidebar:
    MODEL_OPTIONS = ["mistral", "Llama-2-7b", "Mistral-7B"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.5
    TEMPERATURE_STEP = 0.01

    def __init__(self):
        # Ensure default values are set at initialization
        if 'temperature' not in st.session_state:
            st.session_state['temperature'] = self.TEMPERATURE_DEFAULT_VALUE

    @staticmethod
    def show_logo(config):
        # image_path = "./img/rhone-" + config['event']['location'] + ".png"
        # image_path = "./img/fedora_avatar.png"
        image_path = "./img/summit.png"
        st.sidebar.image(image_path, width=200)

    @staticmethod
    def about():
        about = st.sidebar.expander("About 🤖")
        sections = [
            "#### ChatPDF is an advanced AI chatbot equipped with conversational memory capabilities, "
            "specifically crafted to facilitate intuitive discussions and interactions with users regarding their PDF "
            "data."
        ]
        for section in sections:
            about.write(section)

    @staticmethod
    def show_login(config):
        # Initialize the authentication_status key in st.session_state
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None

        authenticator = stauth.Authenticate(
            config['credentials'],
            config['cookie']['name'],
            config['cookie']['key'],
            config['cookie']['expiry_days'],
            config['preauthorized']
        )
        name, authentication_status, username = authenticator.login('Login', 'sidebar')

        # Initialize session state variables
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None
        if 'name' not in st.session_state:
            st.session_state['name'] = None

        # Rest of your authentication logic...

        # Use session state variables for control flow
        if st.session_state["authentication_status"]:
            authenticator.logout('Logout', 'sidebar')
            # st.write(f'Welcome *{st.session_state["name"]}*')
        elif not st.session_state["authentication_status"]:
            st.error('Username/password is incorrect')
        elif st.session_state["authentication_status"] is None:
            st.warning('Please enter your username and password')
        return name, authentication_status, username

    def model_selector(self):
        model = st.selectbox(label="Model", options=self.MODEL_OPTIONS)
        st.session_state["model"] = model

    @staticmethod
    def reset_chat_button():
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True
            st.rerun()
        st.session_state.setdefault("reset_chat", False)

    def temperature_slider(self):
        temperature = st.slider(
            label="Temperature",
            min_value=self.TEMPERATURE_MIN_VALUE,
            max_value=self.TEMPERATURE_MAX_VALUE,
            value=st.session_state['temperature'], 
            step=self.TEMPERATURE_STEP,
        )
        st.session_state["temperature"] = temperature

    def show_options(self):
        # Create a section in the sidebar for options
        with st.sidebar:
            # Display a button to reset chat
            self.reset_chat_button()

            with st.expander("Temperature Control"):
                self.temperature_slider()

            # Set default session state if not already set
            # st.session_state.setdefault("model", self.MODEL_OPTIONS[0])
            st.session_state.setdefault("temperature", self.TEMPERATURE_DEFAULT_VALUE)
