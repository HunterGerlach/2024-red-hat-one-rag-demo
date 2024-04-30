import streamlit as st
from langchain.chains import LLMChain, ConversationalRetrievalChain
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.schema import StrOutputParser
from snowflake import SnowflakeGenerator
from embeddings.doc_embedding import DocEmbedding
from chat_management.chat_history import ChatHistory
import asyncio
from concurrent.futures import ThreadPoolExecutor

executor = ThreadPoolExecutor()

class Chatbot:
    def __init__(self, retriever, llm, history_key="chat_history"):
        self.retriever = retriever
        self.llm = llm
        self.history = ChatHistory(history_key)

    @classmethod
    def initialize_chatbot_if_absent(cls, session_state, pdf, llm, redis_url, history_key="chat_history"):
        """Initialize the chatbot if it's not already present in the session state."""
        if 'chatbot' not in session_state:
            index_generator = SnowflakeGenerator(42)
            index_name = str(next(index_generator))
            print("Index Name: " + index_name)
            chatbot = cls.setup_chatbot(pdf, llm, redis_url, index_name, "redis_schema.yaml", history_key)
            session_state['chatbot'] = chatbot

    @staticmethod
    def setup_chatbot(uploaded_file, llm, redis_url, index_name, schema, chat_history):
        """Sets up the chatbot with the uploaded file, model, and chat history."""
        embeds = DocEmbedding()
        with st.spinner("Initializing the document retriever..."):
            if uploaded_file:
                uploaded_file.seek(0)
                file = uploaded_file.read()
                embeds.create_doc_embedding(file, redis_url, index_name)
                retriever = embeds.get_doc_retriever(redis_url, index_name, schema)
                if retriever:
                    return Chatbot(retriever, llm, chat_history)
                else:
                    st.error("Failed to initialize the document retriever.")
                    return None
            else:
                st.error("Please upload a file to get started.")
                return None

    async def conversational_chat(self, query):

        if not self.retriever:
            st.error("Document retriever is not initialized.")
            return "No retriever available."
        response = await self.async_invoke_llm(query)
        return response

    async def async_invoke_llm(self, query):
        """Invoke the LLM asynchronously."""
        tab1, tab2 = st.tabs(["Chat", "Debug"])

        with tab2:
            # Check if the LLM is initialized
            if self.llm is None:
                st.error("LLM is not initialized.")
                return None

            with st.expander(label="User's Query", expanded=False):
                st.write(query)

            # Retrieve and display documents asynchronously
            docs = await self.retriever.ainvoke(query)
            if docs:
                with st.expander(label="Retrieved Documents", expanded=False):
                    st.write(docs, expanded=False)


                # for doc in docs:
                #     st.write(doc if isinstance(doc, str) else doc.page_content)  # Handle both strings and objects with page_content
            
            # Construct the prompt including the query and documents, only after the documents have been retrieved
            prompt = f"You are an assistant who only responds with three words - no matter what. Literally only three-word responses. How would you respond to: {query}\n\nHere are the documents I found that may be relevant: {[doc if isinstance(doc, str) else doc.page_content for doc in docs]}"
            
            with st.expander(label="Prompt including Query and Documents", expanded=False):
                st.write(prompt)

        with tab1:

            # Stream results and display the output
            st.markdown(f"### Result Stream")
            output_container = st.empty()
            response_buffer = ""  # Buffer to accumulate responses

            # Prepare the prompt for the Runnable interface
            runnable_prompt = RunnablePassthrough(lambda _: query) if isinstance(query, str) else RunnablePassthrough(lambda _: str(query))
            
            # Define the chain for fetching and processing documents
            rag_chain_from_docs = (
                RunnablePassthrough.assign(context=lambda x: "\n\n".join(doc.page_content for doc in x['context']))
                | runnable_prompt
                | self.llm
                | StrOutputParser()
            )

            # Setup a parallel runnable to handle the retrieval (context) and the LLM processing (question)
            rag_chain_with_source = RunnableParallel(
                {"context": self.retriever, "question": runnable_prompt}
            ).assign(answer=rag_chain_from_docs)

            # # # Stream responses from LLM and update the output container continuously
            # # Activate the spinner before starting the streaming process
            # with st.spinner(text=''): #text="Loading... Please wait"):
            #     # Initiate streaming responses from LLM and update the output container continuously
            #     for chunk in self.llm.stream(prompt):
            #         if chunk:
            #             response_buffer += chunk  # Append text to the buffer
            #             output_container.markdown(response_buffer)  # Display updated response in the output container

            response_buffer = ""
            output_container = st.empty()

            with st.spinner(text='Loading... Please wait'):
                for chunk in self.llm.stream(prompt):
                    # Break out of the loop if stop_streaming is True
                    if st.session_state['stop_streaming']:
                        st.session_state['stop_streaming'] = False  # Reset the control
                        break
                    if chunk:
                        response_buffer += chunk  # Append text to the buffer
                        output_container.markdown(response_buffer)
