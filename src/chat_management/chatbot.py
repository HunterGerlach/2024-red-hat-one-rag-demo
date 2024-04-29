import streamlit as st
import os
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import StrOutputParser
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

    # async def conversational_chat(self, query):
    #     """Perform conversational chat using threading for non-async libs."""
    #     def synchronous_chat():
    #         chain = ConversationalRetrievalChain.from_llm(
    #             llm=self.llm,
    #             memory=self.history.history,
    #             retriever=self.rds_retriever
    #         )
    #         return chain({"question": query}, return_only_outputs=True)

    #     loop = asyncio.get_running_loop()
    #     result = await loop.run_in_executor(executor, synchronous_chat)
    #     return result["answer"], self.rds_retriever



    async def conversational_chat(self, query):
        prompt = f"You are an unhelpful assistant. How would you respond to: {query}"
        response = await self.async_invoke_llm(prompt)
        return response

    # async def async_invoke_llm(self, prompt):
    #     # Implement async handling if the underlying method supports it
    #     response_buffer = ""  # Initialize a buffer for accumulating text
    #     for chunk in self.llm._stream(prompt):
    #         if chunk.text:
    #             response_buffer += chunk.text  # Append each chunk to the buffer
    #             st.write(response_buffer)  # Write/update the output with the accumulated buffer
    
    # async def async_invoke_llm(self, prompt):
    #     # Implement async handling if the underlying method supports it
    #     for response in self.llm.stream(prompt):
    #         print(response)
    #         st.write(response)


    async def async_invoke_llm(self, prompt):
        output_container = st.empty()  # Create a mutable placeholder
        response_buffer = ""  # Initialize a buffer to accumulate text

        for chunk in self.llm.stream(prompt):
            if chunk:
                response_buffer += chunk  # Append text to the buffer
                output_container.markdown(response_buffer)  # Update the content of the output container

        # return response



    # async def conversational_chat(self, query):
    #     """Perform conversational chat using threading for non-async libs."""
    #     refined_query = self.refine_query(query)  # Refine the query before sending
    #     result = await self.invoke_llm(refined_query)
    #     return result

    # def refine_query(self, query):
    #     """Modify the query to include additional context or rephrase for clarity."""
    #     # Example: Append historical context from previous interactions
    #     context = self.history.get_recent_context()
    #     refined_query = f"{context}\n\n{query}"
    #     return refined_query

    # async def invoke_llm(self, query):
    #     """Asynchronous call to LLM with refined query."""
    #     def synchronous_chat():
    #         chain = ConversationalRetrievalChain.from_llm(
    #             llm=self.llm,
    #             memory=self.history.history,
    #             retriever=self.rds_retriever
    #         )
    #         return chain({"question": query}, return_only_outputs=True)

    #     loop = asyncio.get_running_loop()
    #     result = await loop.run_in_executor(executor, synchronous_chat)
    #     return result["answer"], self.rds_retriever