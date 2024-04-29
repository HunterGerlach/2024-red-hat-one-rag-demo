import os

import streamlit as st

from chat_management.chatbot import Chatbot
from chat_management.chat_history import ChatHistory
from ui_components.layout import Layout
from ui_components.sidebar import Sidebar, Utilities
from config_manager import ConfigManager
from model_services.model_comparison import ModelComparison
from snowflake import SnowflakeGenerator
from langchain.schema import HumanMessage, AIMessage
from vector_db.redis_manager import RedisManager
from model_services.model_factory import ModelFactory

def initialize_default_session_variables():
    """Set default values for session variables."""
    default_values = {
        'ready': False,
        'authentication_status': False,
        'reset_chat': False
    }
    for key, value in default_values.items():
        st.session_state.setdefault(key, value)

def manage_responses(history, response_container, prompt_container, model_comparison, model_configs):
    is_ready, user_input, submit_button = layout.prompt_form()
    if is_ready:
        output, embeddings = st.session_state["chatbot"].conversational_chat(user_input)

        # Simulate 4 different model outputs (actually the same for now)
        model_names = ["Model 1", "Model 2", "Model 3", "Model 4"]
        try:
            # Generate a full conversation for the simulation
            full_conversation = history.get_full_conversation()
            full_conversation_histories = {
                model_name: full_conversation for model_name in model_names
            }
            # Now display the full conversation for each model
            ModelComparison.display_model_comparison_results(model_comparison, full_conversation_histories)
            history.generate_messages(response_container)
        except Exception as e:
            st.error(f"Error during model comparisons: {e}")
    if st.session_state["reset_chat"]:
        history.reset()      

def load_and_validate_config():
    """Load and validate configuration, return configs if valid, otherwise stop the app."""
    configs = ConfigManager.load_config_details()
    if not ConfigManager.validate_configurations(configs):
        st.stop()
    return configs

def initialize_ui(configs):
    """Initialize the UI components and return layout and sidebar."""
    st.set_page_config(layout="wide", page_icon="🐶", page_title="Red Hat - Summit - InstructLab Demo")
    layout = Layout()
    sidebar = Sidebar()
    layout.show_header()
    sidebar.show_logo(configs)
    return layout, sidebar

def main_application_logic(configs, layout, sidebar):
    """Handle the main application logic."""
    redis_url = RedisManager.build_redis_connection_url(configs['redis'])
    llm = ModelFactory.create_inference_model(configs['inference_server'])

    sidebar.show_login(configs)
    if st.session_state["authentication_status"]:
        process_authenticated_user_flow(configs, layout, sidebar, llm, redis_url)

def process_authenticated_user_flow(configs, layout, sidebar, llm, redis_url):
    """Process the flow for an authenticated user."""
    try:
        pdf, doc_content = Utilities.handle_file_upload()
        if pdf:
            st.header("GenAI Architecture Comparison Tool")
            sidebar.show_options()

            model_comparison = ModelComparison(number_of_models=4)
            model_configs = model_comparison.collect_model_configs()
            
            Chatbot.initialize_chatbot_if_absent(
                session_state=st.session_state,
                pdf=pdf, 
                llm=llm, 
                redis_url=redis_url,
                history_key="chat_history"
            )

            st.success("Document successfully embedded in vector database. Chatbot initialized successfully.")
            st.session_state["ready"] = True

            history_model_1 = ChatHistory(history_key="chat_history")
            response_container, prompt_container = st.container(), st.container()
            manage_responses(history_model_1, response_container, prompt_container, model_comparison, model_configs)
    except Exception as e:
        st.error(f"Unexpected error during PDF upload or processing: {e}")
        st.stop()


if __name__ == '__main__':
    initialize_default_session_variables()
    configs = load_and_validate_config()
    layout, sidebar = initialize_ui(configs)
    main_application_logic(configs, layout, sidebar)
    sidebar.about()
