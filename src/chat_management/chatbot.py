import streamlit as st
import os
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate
from snowflake import SnowflakeGenerator

from chat_management.chat_history import ChatHistory

class Chatbot:
    """
    Class to manage chatbot operations.
    """
    def __init__(self, rds_retriever, llm, history_key="chat_history"):
        self.rds_retriever = rds_retriever
        self.llm = llm
        self.history = ChatHistory(history_key)

    def initialize_chatbot_if_absent(session_state, utils, pdf, llm, redis_url, history_key="chat_history"):
        """Initialize the chatbot if it's not already present in the session state."""
        if 'chatbot' not in session_state:
            index_generator = SnowflakeGenerator(42)
            index_name = str(next(index_generator))
            print("Index Name: " + index_name)
            chat_history = ChatHistory(history_key)
            chatbot = utils.setup_chatbot(pdf, llm, redis_url, index_name, "redis_schema.yaml", chat_history.history)
            session_state["chatbot"] = chatbot

    def conversational_chat(self, query):
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            memory=self.history.history,
            retriever=self.rds_retriever
        )

        result = chain({"question": query}, return_only_outputs=True)

        return result["answer"], self.rds_retriever
