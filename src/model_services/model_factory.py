import os
from langchain_community.llms import HuggingFaceTextGenInference, Ollama

class ModelFactory:
    """ Factory class for creating inference models. """

    @staticmethod
    def create_inference_model(inference_config):
        """Create and return an inference model based on the provided configuration."""
        model_type = inference_config.get("type", "ollama")
        if model_type == "ollama":
            return Ollama(model="mixtral") # jefferyb/granite
        else:
            return HuggingFaceTextGenInference(
                inference_server_url=os.getenv('INFERENCE_SERVER_URL', inference_config["url"]),
                max_new_tokens=int(os.getenv('MAX_NEW_TOKENS', '20')),
                top_k=int(os.getenv('TOP_K', '3')),
                top_p=float(os.getenv('TOP_P', '0.95')),
                typical_p=float(os.getenv('TYPICAL_P', '0.95')),
                temperature=float(os.getenv('TEMPERATURE', '0.9')),
                repetition_penalty=float(os.getenv('REPETITION_PENALTY', '1.01')),
                streaming=True,
                verbose=False
            )