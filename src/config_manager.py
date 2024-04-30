import yaml
import os
import streamlit as st
from model_services.model_config import ModelConfig

class ConfigManager:
    """ Manages application configuration. """
    
    @staticmethod
    def load_config_details():
        """ Load configuration details from a YAML file. """
        config_path = os.getenv('CONFIG_PATH', 'config.yaml')
        try:
            with open(config_path, 'r') as config_file:
                configurations = yaml.safe_load(config_file)
            return configurations
        except FileNotFoundError:
            st.error("Configuration file not found.")
            return None
        except yaml.YAMLError as exc:
            st.error(f"Error parsing configuration file: {exc}")
            return None

    @staticmethod
    def validate_configurations(configurations):
        """ Validate that the configuration is not empty and return a boolean. """
        is_valid = bool(configurations) and all(key in configurations for key in ["redis", "inference_server"])
        if not is_valid:
            st.error("Configuration details are missing or incomplete.")
        return is_valid
    
    @staticmethod
    def get_model_configs():
        """ Retrieve model configurations from the YAML file. """
        configs = ConfigManager.load_config_details()
        if configs and 'architectures' in configs:
            return [ModelConfig(
                name=arch['name'],
                description=arch['description'],
                endpoint=arch['endpoint'],
                uses_rag=arch['uses_rag'],
                model_name=arch['model_name']) for arch in configs['architectures']]
        else:
            st.error("Model configurations are missing or incomplete.")
            return []
