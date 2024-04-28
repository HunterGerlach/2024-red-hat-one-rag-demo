import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import tempfile

from chat_management.chatbot import Chatbot
from embeddings.doc_embedding import DocEmbedding

class Utilities:    
    def read_pdf(file):
        import PyPDF2
        reader = PyPDF2.PdfReader(file)
        text = []
        for page in reader.pages:
            text.append(page.extract_text())
        return "\n".join(text)

    def read_text(file):
        return file.getvalue().decode("utf-8")

    def read_docx(file):
        import docx
        doc = docx.Document(file)
        text = [paragraph.text for paragraph in doc.paragraphs]
        return "\n".join(text)
    

    @staticmethod
    def attempt_pdf_upload(upload_handler):
        """Upload a PDF and return file and content if successful, or None otherwise."""
        pdf_file, content = upload_handler()
        if not pdf_file:
            st.info("Upload a PDF file to get started", icon="👈")
            return None, None
        return pdf_file, content

    @staticmethod
    def handle_upload():
        """
        Handles the file upload and displays the uploaded file
        """
        uploaded_file = st.sidebar.file_uploader("upload", type="pdf", label_visibility="collapsed")#| st.file_uploader("upload", type="text", label_visibility="collapsed") | st.sidebar.file_uploader("upload", type="docx", label_visibility="collapsed")
        doc_content = ""
        if uploaded_file is not None:
            if uploaded_file.type == "application/pdf":
                doc_content = Utilities.read_pdf(uploaded_file)
            elif uploaded_file.type == "text/plain":
                doc_content = Utilities.read_text(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc_content = Utilities.read_docx(uploaded_file)
        else:
            st.sidebar.info(
                "Upload a PDF file to get started", icon="👆"
            )
            st.session_state["reset_chat"] = True
        return uploaded_file, doc_content

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
