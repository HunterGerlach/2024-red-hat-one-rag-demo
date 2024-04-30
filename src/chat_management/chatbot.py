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
        st.error("Please upload a file to get started.")
        return None

    async def conversational_chat(self, query):
        if not self.retriever:
            st.error("Document retriever is not initialized.")
            return "No retriever available."
        response = await self.async_invoke_llm(query)
        return response

    async def a2sync_invoke_llm(self, prompt):
        if not self.llm:
            st.error("LLM is not initialized.")
            return "LLM not initialized."
        # 1 response
        # 2 input

           #     # Ensure that the prompt is correctly formatted before passing it to the chain
    #     runnable_prompt = RunnablePassthrough(lambda _: prompt) if isinstance(prompt, str) else RunnablePassthrough(lambda _: str(prompt))

    #     rag_chain_from_docs = (
    #         RunnablePassthrough.assign(context=(lambda x: "\n\n".join(doc.page_content for doc in x['context'])))
    #         | runnable_prompt
    #         | self.llm
    #         | StrOutputParser()
    #     )

    #     rag_chain_with_source = RunnableParallel(
    #         {"context": self.retriever, "question": runnable_prompt}
    #     ).assign(answer=rag_chain_from_docs)

    #     for chunk in rag_chain_with_source.stream(prompt):
    #         if chunk:
    #             response_buffer += chunk
    #             output_container.markdown(response_buffer)


        output_container = st.empty()  # Create a mutable placeholder
        response_buffer = ""  # Initialize a buffer to accumulate text

        for chunk in self.llm.stream(prompt):
            if chunk:
                response_buffer += chunk  # Append text to the buffer
                output_container.markdown(response_buffer)  # Update the content of the output container


        output_container = st.empty()
        response_buffer = ""

        runnable_prompt = RunnablePassthrough(lambda _: {"question": prompt})
        runnable_context = RunnablePassthrough(lambda x: {"context": self.retriever.search(x["question"])})

        # Use a parallel runnable to process context and question simultaneously
        rag_chain = RunnableParallel(
            {"context": runnable_context, "question": runnable_prompt}
        ) | self.llm | StrOutputParser()

        try:
            async for result in rag_chain.astream({"question": prompt}):
                response_buffer += result['answer']  # Assuming 'answer' is part of the output dictionary
                output_container.markdown(response_buffer)
        except Exception as e:
            st.error(f"An error occurred during streaming: {str(e)}")

        if not response_buffer:
            st.error("No response was generated. Please check the configuration and input.")

    # streaming
    # async def a3sync_invoke_llm(self, prompt):
    #     if not self.llm:
    #         st.error("LLM is not initialized.")
    #         return "LLM not initialized."
        
        # output_container = st.empty()  # Create a mutable placeholder for streaming output
        # response_buffer = ""  # Initialize a buffer to accumulate text responses

        # Stream responses from LLM and update the output container continuously
        for chunk in self.llm.stream(prompt):
            if chunk:
                response_buffer += chunk  # Append text to the buffer
                output_container.markdown(response_buffer)  # Display updated response in the output container

        # Additional runnable chain for using retriever and LLM in a parallel setup
        runnable_prompt = RunnablePassthrough(lambda _: {"question": prompt})
        runnable_context = RunnablePassthrough(lambda x: {"context": self.retriever.search(x["question"])})

        # Define a parallel runnable to process context and question simultaneously
        rag_chain = RunnableParallel(
            {"context": runnable_context, "question": runnable_prompt}
        ) | self.llm | StrOutputParser()

        # Stream results asynchronously and handle potential exceptions
        try:
            async for result in rag_chain.astream({"question": prompt}):
                response_buffer += result['answer']  # Assuming 'answer' is part of the output dictionary
                output_container.markdown(response_buffer)
        except Exception as e:
            st.error(f"An error occurred during streaming: {str(e)}")

        # Handle case where no response was generated
        if not response_buffer:
            st.error("No response was generated. Please check the configuration and input.")

    # # prompt and context
    # async def a4sync_invoke_llm(self, prompt):
    #     if self.llm is None:
    #         st.error("LLM is not initialized.")
    #         return None

        # output_container = st.empty()  # Placeholder for output
        # response_buffer = ""  # Buffer to hold response text

        # Ensure the prompt is correctly formatted before processing
        # runnable_prompt = RunnablePassthrough(lambda _: prompt) if isinstance(prompt, str) else RunnablePassthrough(lambda _: str(prompt))

        # Setup a chain from retrieved documents to LLM processing
        # rag_chain_from_docs = (
        #     RunnablePassthrough.assign(context=(lambda x: "\n\n".join(doc.page_content for doc in x['context'])))
        #     | runnable_prompt
        #     | self.llm
        #     | StrOutputParser()
        # )

        # # Define a parallel runnable to handle retrieval and LLM processing
        # rag_chain_with_source = RunnableParallel(
        #     {"context": self.retriever, "question": runnable_prompt}
        # ).assign(answer=rag_chain_from_docs)

        # Stream the response and update the output container
        # for chunk in rag_chain_with_source.stream("What is Task Decomposition"):
        #     if chunk:
        #         response_buffer += chunk
        #         output_container.markdown(response_buffer)

    async def asy4nc_invoke_llm(self, prompt):
        if self.llm is None:
            st.error("LLM is not initialized.")
            return None

        output_container = st.empty()  # Placeholder for output
        response_buffer = ""  # Buffer to hold response text

        runnable_prompt = RunnablePassthrough(lambda _: prompt) if isinstance(prompt, str) else RunnablePassthrough(lambda _: str(prompt))
        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=(lambda x: "\n\n".join(doc.page_content for doc in x['context'])))
            | runnable_prompt
            | self.llm
            | StrOutputParser()
        )

        # Define a parallel runnable to handle retrieval and LLM processing
        rag_chain_with_source = RunnableParallel(
            {"context": self.retriever, "question": runnable_prompt}
        ).assign(answer=rag_chain_from_docs)

        # Stream the response and update the output container
        for chunk in rag_chain_with_source.stream(prompt):
            # if chunk:
                response_buffer += chunk
                output_container.markdown(response_buffer)

        # Define a parallel runnable to handle retrieval and LLM processing
        # rag_chain_with_source = RunnableParallel(
        #     {"context": self.retriever, "question": runnable_prompt}
        # ).assign(answer=rag_chain_from_docs)
        
        # output_container.markdown(prompt)
        # output_container.markdown(str(self.retriever))  # Convert the retriever object to string for display
    # Assuming existence of 'st' for Streamlit and 'self.llm.stream' method for LLM processing


    async def streaming_good_async_invoke_llm(self, query):
        # Check if the LLM is initialized
        if self.llm is None:
            st.error("LLM is not initialized.")
            return None

        prompt_container = st.empty()  # Placeholder for input
        query_container = st.empty()  # Placeholder for output
        vector_container = st.empty()  # Placeholder for vector output
        output_container = st.empty()
        response_buffer = ""  # Buffer to accumulate responses

        prompt = f"You are an assistant who only responds with a single word no matter what. Literally only one word responses. How would you respond to: {query}"

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

        prompt_container.markdown(prompt)
        query_container.markdown(query)
        
        # for chunk in rag_chain_with_source.stream(prompt):
        #     # if chunk:
        #         response_buffer += chunk
        #         vector_container.markdown(response_buffer)

        # Stream responses from LLM and update the output container continuously
        for chunk in self.llm.stream(prompt):
            if chunk:
                response_buffer += chunk  # Append text to the buffer
                output_container.markdown(response_buffer)  # Display updated response in the output container


    async def formatting_good_async_invoke_llm(self, query):
        if self.llm is None:
            st.error("LLM is not initialized.")
            return None

        # Display the prompt and query in the UI
        prompt = f"You are an assistant who only responds with a single word no matter what. Literally only one word responses. How would you respond to: {query}"
        st.markdown(f"### Prompt")
        st.write(prompt)
        st.markdown(f"### Query")
        st.write(query)

        # Retrieve and display documents asynchronously
        docs = await self.retriever.ainvoke(query)
        if docs:
            st.markdown(f"### Retrieved Documents")
            for doc in docs:
                st.write(doc if isinstance(doc, str) else doc.page_content)  # Handle both strings and objects with page_content

        # Correct handling of the context assuming it's already in the correct format
        context_strings = [doc if isinstance(doc, str) else doc.page_content for doc in docs]

        # Process and stream results separately
        await self.process_and_stream(query, context_strings)

    async def process_and_stream(self, query, context_strings):
        # Define the chain for fetching and processing documents
        runnable_prompt = RunnablePassthrough(lambda _: query)
        rag_chain_from_docs = (
            RunnablePassthrough.assign(context=lambda x: "\n\n".join(x['context']))
            | runnable_prompt
            | self.llm
            | StrOutputParser()
        )

        # Setup a parallel runnable (if needed)
        rag_chain_with_source = RunnableParallel(
            {"context": context_strings, "question": runnable_prompt}
        ).assign(answer=rag_chain_from_docs)

        # Stream results and display the output
        st.markdown(f"### Result Stream")
        output_container = st.empty()
        async for chunk in self.stream_async(rag_chain_from_docs.stream({"context": context_strings, "question": query})):
            output_container.write(chunk)

    async def stream_async(self, iterator):
        """
        Converts a synchronous generator to an asynchronous iterator if needed.
        """
        for item in iterator:
            yield item
            await asyncio.sleep(0)  # Allow loop interruption



    async def async_invoke_llm(self, query):
        # Check if the LLM is initialized
        if self.llm is None:
            st.error("LLM is not initialized.")
            return None

        st.markdown(f"### User's Query")
        st.write(query)

        # Retrieve and display documents asynchronously
        docs = await self.retriever.ainvoke(query)
        if docs:
            st.markdown(f"### Retrieved Documents")
            for doc in docs:
                st.write(doc if isinstance(doc, str) else doc.page_content)  # Handle both strings and objects with page_content
        
        # Construct the prompt including the query and documents, only after the documents have been retrieved
        prompt = f"You are an assistant who only responds with a single word no matter what. Literally only one word responses. How would you respond to: {query}\n\nHere are the documents I found that may be relevant: {[doc if isinstance(doc, str) else doc.page_content for doc in docs]}"
        st.markdown(f"### Prompt including Query and Documents")
        st.write(prompt)


        # prompt_container = st.empty()  # Placeholder for input
        # query_container = st.empty()  # Placeholder for output
        # vector_container = st.empty()  # Placeholder for vector output


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

        # prompt_container.markdown(prompt)
        # query_container.markdown(query)
        
        # for chunk in rag_chain_with_source.stream(prompt):
        #     # if chunk:
        #         response_buffer += chunk
        #         vector_container.markdown(response_buffer)

        # Stream responses from LLM and update the output container continuously
        for chunk in self.llm.stream(prompt):
            if chunk:
                response_buffer += chunk  # Append text to the buffer
                output_container.markdown(response_buffer)  # Display updated response in the output container