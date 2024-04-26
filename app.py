import os

import streamlit as st
from langchain.llms import HuggingFaceTextGenInference
from langchain.llms import Ollama
from langchain.prompts import PromptTemplate

from gui.history import ChatHistory
from gui.layout import Layout
from gui.sidebar import Sidebar, Utilities
from gui.model_comparison import ModelComparison
from snowflake import SnowflakeGenerator

if __name__ == '__main__':
    st.set_page_config(layout="wide", page_icon="💬", page_title="ChatPDF")
    layout, sidebar, utils = Layout(), Sidebar(), Utilities()
    configs = utils.load_config_details()
    
    username = configs["redis"]["username"]
    password = configs["redis"]["password"]
    host = configs["redis"]["host"]
    port = configs["redis"]["port"]
    redis_url = f"redis://{username}:{password}@{host}:{port}"

    inference_server_url= configs["inference_server"]["url"]


    layout.show_header()
    if not configs:
        layout.show_loging_details_missing()
    else:
        
        sidebar.show_logo(configs)
        sidebar.show_login(configs)
        pdf, doc_content = utils.handle_upload()

        if pdf:
            sidebar.show_options()

            st.header("Model Comparison Tool")
            model_comparison = ModelComparison(number_of_models=4)  # Configure for 3 models
            model_comparison.display_model_comparison()
            # show_all_chunks, show_full_doc = layout.advanced_options()

            # Assume 'doc' and 'index' are variables holding your document content and indexed data
            # doc = "This is the full document content..."
            # index = "Index details here..."
            # Assuming the doc_content is filled
            doc = doc_content
            index = ""

            # if show_full_doc:
            #     with st.expander("Full Document Contents"):
            #         st.text(doc)  # Show full document contents

            # if show_all_chunks:
            #     with st.expander("Vector Results"):
            #         st.text(index)  # Show details of the indexed chunks or embedding results

            try:
                if 'chatbot' not in st.session_state:
                    
                    if configs["inference_server"]["type"] == "ollama":
                        llm = Ollama(model="mistral")
                    else:
                        llm = HuggingFaceTextGenInference(
                            inference_server_url=os.environ.get('INFERENCE_SERVER_URL'),
                            max_new_tokens=int(os.environ.get('MAX_NEW_TOKENS', '512')),
                            top_k=int(os.environ.get('TOP_K', '3')),
                            top_p=float(os.environ.get('TOP_P', '0.95')),
                            typical_p=float(os.environ.get('TYPICAL_P', '0.95')),
                            temperature=float(os.environ.get('TEMPERATURE', '0.9')),
                            repetition_penalty=float(os.environ.get('REPETITION_PENALTY', '1.01')),
                            streaming=False,
                            verbose=False
                        )
                    
                    indexGenerator = SnowflakeGenerator(42)
                    index_name = str(next(indexGenerator))
                    print("Index Name: " + index_name)
                    index = index_name
                    
                    chatbot = utils.setup_chatbot(pdf, llm, redis_url, index_name, "redis_schema.yaml")
                    st.session_state["chatbot"] = chatbot

                # if st.session_state.get("ready"):
                #     history = ChatHistory()
                #     history.initialize(pdf.name)

                #     response_container, prompt_container = st.container(), st.container()
                #     with prompt_container:
                #         user_input = st.text_input("Ask a question:", key="user_query")
                #         if st.button("Ask"):
                #             results = st.session_state["chatbot"].conversational_chat(user_input)
                #             for model_name, answer in results.items():
                #                 with response_container:
                #                     st.markdown(f"### Response from {model_name}")
                #                     st.write(answer)


                if st.session_state["ready"]:
                    history = ChatHistory()
                    history.initialize(pdf.name)

                    response_container, prompt_container = st.container(), st.container()

                    with prompt_container:
                        is_ready, user_input = layout.prompt_form()

                        if st.session_state["reset_chat"]:
                            history.reset()

                        if is_ready:
                            with st.spinner("Processing query..."):
                                output, embeddings = st.session_state["chatbot"].conversational_chat(user_input)
                                index = embeddings
                    history.generate_messages(response_container)

            except Exception as e:
                st.error(f"{e}")
                st.stop()

    sidebar.about()
