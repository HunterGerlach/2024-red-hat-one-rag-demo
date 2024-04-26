import streamlit as st


class Layout:

    def show_header(self):
        """
        Displays the header of the app
        """
        st.markdown(
            """
            <h2 style='text-align: center;'>Red Hat IT - Summit - InstructLab Demo 🐶</h1>
            """,
            unsafe_allow_html=True,
        )

    def show_loging_details_missing(self):
        """
        Displays a message if the user has not entered an API key
        """
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Please config your credentials to start chatting.</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

    def prompt_form(self):
        """
        Displays the prompt form
        """
        with st.form(key="my_form", clear_on_submit=True):
            user_input = st.text_area(
                "Query:",
                placeholder="Ask me anything about the PDF...",
                key="input",
                label_visibility="collapsed",
            )
            submit_button = st.form_submit_button(label="Send")

            is_ready = submit_button and user_input
        return is_ready, user_input
    
    def advanced_options(self):
        with st.expander("Advanced Options"):
            show_all_chunks = st.checkbox("Show all chunks retrieved from vector search")
            show_full_doc = st.checkbox("Show parsed contents of the document")
        return show_all_chunks, show_full_doc