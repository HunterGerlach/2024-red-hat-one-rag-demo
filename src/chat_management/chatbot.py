import streamlit as st
import os
from langchain.chains import ConversationalRetrievalChain
from snowflake import SnowflakeGenerator
from utils.utilities import Utilities
from embeddings.doc_embedding import DocEmbedding
from chat_management.chat_history import ChatHistory

class Chatbot:
    """
    Class to manage chatbot operations.
    """
    def __init__(self, rds_retriever, llm, history_key="chat_history"):
        self.rds_retriever = rds_retriever
        self.llm = llm
        self.history = ChatHistory(history_key)


    @staticmethod
    def setup_chatbot(uploaded_file, llm, redis_url, index_name, schema, chat_history):
        """
        Sets up the chatbot with the uploaded file, model, and chat history
        """
        embeds = DocEmbedding()
        with st.spinner("Embedding document..."):
            if uploaded_file is None:
                st.error("Please upload a file to get started.")
                return None
            uploaded_file.seek(0)
            file = uploaded_file.read()

            embeds.create_doc_embedding(file, redis_url, index_name)

            retriever = embeds.get_doc_retriever(redis_url, index_name, schema)
            chatbot = Chatbot(retriever, llm)
            print(f"new chatbot is created with {index_name} {schema}.")
        st.session_state["ready"] = True
        return chatbot

    @classmethod
    def initialize_chatbot_if_absent(cls, session_state, pdf, llm, redis_url, history_key="chat_history"):
        """Initialize the chatbot if it's not already present in the session state."""
        if 'chatbot' not in session_state:
            index_generator = SnowflakeGenerator(42)
            index_name = str(next(index_generator))
            print("Index Name: " + index_name)
            chat_history = ChatHistory(history_key)
            chatbot = Chatbot.setup_chatbot(pdf, llm, redis_url, index_name, "redis_schema.yaml", chat_history)
            session_state["chatbot"] = chatbot

    def conversational_chat(self, query):
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            memory=self.history.history,
            retriever=self.rds_retriever
        )
        result = chain({"question": query}, return_only_outputs=True)
        return result["answer"], self.rds_retriever
