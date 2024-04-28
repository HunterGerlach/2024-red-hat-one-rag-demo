import streamlit as st
import os
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate


class Chatbot:

    def __init__(self, rds_retriever, llm):
        self.rds_retriever = rds_retriever
        self.llm = llm

    def conversational_chat(self, query):
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            memory=st.session_state["history"],
            retriever=self.rds_retriever
        )

        result = chain({"question": query}, return_only_outputs=True)

        return result["answer"], self.rds_retriever
