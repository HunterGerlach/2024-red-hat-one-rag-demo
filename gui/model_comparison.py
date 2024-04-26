import streamlit as st

class ModelComparison:
    def __init__(self, number_of_models=4):
        self.number_of_models = number_of_models
        # Dictionary mapping model types to their respective endpoints
        self.model_endpoints = {
            'Base Model': 'http://0.0.0.0:11434',
            'Base Model + RAG': 'https://api.ollama.ai/base-rag',
            'InstructLab-Aligned Model': 'https://api.ollama.ai/instruct-aligned',
            'InstructLab-Aligned Model + RAG': 'https://api.ollama.ai/instruct-rag'
        }
        # Redis connection setup would normally go here
        self.redis_client = None  # Placeholder for Redis client

    def display_model_comparison(self):
        model_configs = self.collect_model_configs()
        if st.button("Run Comparison"):
            results = self.run_model_comparisons(model_configs)
            self.display_results(results)

    def collect_model_configs(self):
        cols = st.columns(self.number_of_models)
        model_configs = []
        model_options = list(self.model_endpoints.keys())
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"#### Architecture {i+1} Configuration")
                model_type = st.selectbox("Architecture", model_options, index=i, key=f"model_type_{i}")
                st.write("Endpoint:", self.model_endpoints[model_type])
                # Optionally display Redis usage if applicable
                if model_type.endswith('+ RAG') and (i == 1 or i == 3):
                    st.write("Using Redis for RAG/Vector Search")
                model_configs.append(model_type)
        return model_configs

    def run_model_comparisons(self, model_configs):
        results = []
        for i, model_type in enumerate(model_configs):
            endpoint = self.model_endpoints[model_type]
            if model_type.endswith('+ RAG') and (i == 1 or i == 3):
                # Simulate Redis operation for RAG/Vector Search
                result = self.run_redis_operations(model_type, endpoint)
            else:
                result = f"Result from {model_type} at {endpoint}"
            results.append(result)
        return results

    def run_redis_operations(self, model_type, endpoint):
        # Placeholder for Redis-based operations
        # This function would handle RAG or vector searches using Redis
        return f"Result from {model_type} with Redis-based vector search at {endpoint}"

    def display_results(self, results):
        cols = st.columns(self.number_of_models)
        for idx, result in enumerate(results):
            with cols[idx]:
                st.write(result)
        columns = st.columns(len(results))
        for (col, (model_name, answer)) in zip(columns, results.items()):
            with col:
                st.markdown(f"### Response from {model_name}")
                st.write(answer)

