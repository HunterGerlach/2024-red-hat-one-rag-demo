import streamlit as st
import os
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate

from chat_management.chat_history import ChatHistory

class Chatbot:
    """
    Class to manage chatbot operations.
    """
    def __init__(self, rds_retriever, llm, history_key="chat_history"):
        self.rds_retriever = rds_retriever
        self.llm = llm
        self.history = ChatHistory(history_key)

    def conversational_chat(self, query):
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            memory=self.history.history,
            retriever=self.rds_retriever
        )

        result = chain({"question": query}, return_only_outputs=True)

        return result["answer"], self.rds_retriever
