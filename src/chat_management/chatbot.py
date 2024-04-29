import streamlit as st
import os
from langchain.chains import ConversationalRetrievalChain
from snowflake import SnowflakeGenerator
from utils.utilities import Utilities
from embeddings.doc_embedding import DocEmbedding
from chat_management.chat_history import ChatHistory
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

class Chatbot:
    """
    Class to manage chatbot operations.
    """
    def __init__(self, rds_retriever, llm, history_key="chat_history"):
        self.rds_retriever = rds_retriever
        self.llm = llm
        self.history = ChatHistory(history_key)

    @classmethod
    def initialize_chatbot_if_absent(cls, session_state, pdf, llm, redis_url, history_key="chat_history"):
        """Initialize the chatbot if it's not already present in the session state."""
        if 'chatbot' not in session_state:
            index_generator = SnowflakeGenerator(42)
            index_name = str(next(index_generator))
            print("Index Name: " + index_name)
            chatbot = Chatbot.setup_chatbot(pdf, llm, redis_url, index_name, "redis_schema.yaml", history_key)
            session_state["chatbot"] = chatbot

    @staticmethod
    def setup_chatbot(uploaded_file, llm, redis_url, index_name, schema, chat_history):
        """Sets up the chatbot with the uploaded file, model, and chat history."""
        embeds = DocEmbedding()
        if uploaded_file:
            uploaded_file.seek(0)
            file = uploaded_file.read()
            embeds.create_doc_embedding(file, redis_url, index_name)
            retriever = embeds.get_doc_retriever(redis_url, index_name, schema)
            return Chatbot(retriever, llm, chat_history)
        st.error("Please upload a file to get started.")
        return None

    async def conversational_chat(self, query):
        """Perform conversational chat using threading for non-async libs."""
        def synchronous_chat():
            chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                memory=self.history.history,
                retriever=self.rds_retriever
            )
            return chain({"question": query}, return_only_outputs=True)

        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(executor, synchronous_chat)
        return result["answer"], self.rds_retriever