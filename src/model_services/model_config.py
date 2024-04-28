class ModelConfig:
    """
    Class to store model configuration details.
    """
    def __init__(self, name, description, endpoint, uses_rag, model_name=None):
        self.name = name
        self.description = description
        self.endpoint = endpoint
        self.uses_rag = uses_rag
        self.model_name = model_name