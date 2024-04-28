import streamlit as st
import threading
from model_services.model_config import ModelConfig

class ModelComparison:
    """
    Class to manage model comparison operations.
    """
    def __init__(self, number_of_models=4):
        self.number_of_models = number_of_models
        self.all_models = [
            ModelConfig('Base Model', 'A baseline model', 'http://0.0.0.0:11434', False, 'granite-7b'),
            ModelConfig('Base Model + RAG', 'Baseline model with RAG', 'https://api.ollama.ai/base-rag', True, 'granite-7b'),
            ModelConfig('InstructLab-Aligned Model', 'Instruct model with alignments', 'https://api.ollama.ai/instruct-aligned', False, 'granite-7b-instruct-aligned'),
            ModelConfig('InstructLab-Aligned Model + RAG', 'Instruct model with alignments and RAG', 'https://api.ollama.ai/instruct-rag', True, 'granite-7b-instruct-aligned')
        ]

    def display_model_configs(self, model_configs):
        cols = st.columns(self.number_of_models)
        for i, col in enumerate(cols):
            with col:
                model_config = model_configs[i]
                st.markdown(f"#### Architecture {i+1} Configuration")
                st.write("Endpoint:", model_config.endpoint)
                st.write("Description:", model_config.description)
                st.write("Performing RAG:", model_config.uses_rag)
                st.write("Model Name:", model_config.model_name)

    def collect_model_configs(self):
        cols = st.columns(self.number_of_models)
        model_configs = []
        model_options = {model.name: model for model in self.all_models}
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"#### Architecture {i+1} Configuration")
                selected_model_name = st.selectbox(
                    "Choose Architecture", 
                    list(model_options.keys()), 
                    index=i, 
                    key=f"model_select_{i}"
                )
                selected_model = model_options[selected_model_name]
                st.write("Endpoint:", selected_model.endpoint)
                st.write("Description:", selected_model.description)
                st.write("Performing RAG:", selected_model.uses_rag)
                st.write("Model Name:", selected_model.model_name)
                model_configs.append(selected_model)
        return model_configs

    def run_model_comparisons(self, model_configs):
        results = {}
        for model in model_configs:
            if model.uses_rag:
                result = self.run_redis_operations(model)
            else:
                result = f"Result from {model.name} at {model.endpoint}"
            results[model.name] = result
        return results

    def run_redis_operations(self, model):
        return f"Result from {model.name} with Redis-based vector search at {model.endpoint}"

    # def display_results(self, results):
    #     cols = st.columns(len(results))
    #     for col, (model_name, messages) in zip(cols, results.items()):
    #         with col:
    #             st.markdown(f"### Full Conversation from {model_name}")
    #             for msg in messages:  # messages is now a list of strings
    #                 st.write(msg)

    # def display_results(self, results):
    #     cols = st.columns(len(results))
    #     for col, (model_name, messages) in zip(cols, results.items()):
    #         with col:
    #             st.markdown(f"### Full Conversation from {model_name}")
    #             # Use markdown for each message to format it correctly
    #             for msg in messages:  # Assuming msg is a string
    #                 # Use triple backticks for block code formatting or other markdown syntax as needed
    #                 st.markdown(f"```\n{msg}\n```")

    def display_results(self, results):
        cols = st.columns(len(results))
        for col, (model_name, messages) in zip(cols, results.items()):
            with col:
                st.markdown(f"### Full Conversation from {model_name}")
                for msg in messages:
                    # Extract the message content after the "content=" part
                    # Assuming each message is a string that starts with "content='...'"

                    # Find the start of the actual content, add len("content=") to get the starting index
                    start_idx = msg.find("content=") + len("content=")
                    # Extract the message, trimming the quotes
                    message_content = msg[start_idx:].strip("'")

                    # Display the message content
                    st.write(message_content)  # You can use st.markdown if you need markdown formatting

    def run_model_comparisons(model_comparison_tool, model_configs):
        """Run model comparisons and return the results."""
        return model_comparison_tool.run_model_comparisons(model_configs)

    def display_model_comparison_results(model_comparison_tool, results):
        """Display the results of model comparisons."""
        model_comparison_tool.display_results(results)

